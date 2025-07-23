import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { documentsAPI, qaAPI } from '../services/api';
import {
  DocumentTextIcon,
  QuestionMarkCircleIcon,
  UserGroupIcon,
  ChartBarIcon,
  PlusIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { user, hasMinimumRole } = useAuth();
  const { UserRole } = require('../types');

  // Fetch documents
  const { data: documentsData, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsAPI.getDocuments({ limit: 5 }),
  });

  // Fetch Q&A stats
  const { data: qaStats, isLoading: statsLoading } = useQuery({
    queryKey: ['qa-stats'],
    queryFn: () => qaAPI.getStats(),
  });

  const stats = [
    {
      name: 'Total Documents',
      value: qaStats?.total_documents || 0,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Documents',
      value: qaStats?.active_documents || 0,
      icon: DocumentTextIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Total Chunks',
      value: qaStats?.total_chunks || 0,
      icon: ChartBarIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'FAISS Index Size',
      value: qaStats?.faiss_index?.total_chunks || 0,
      icon: ChartBarIcon,
      color: 'bg-orange-500',
    },
  ];

  const quickActions = [
    {
      name: 'Upload Document',
      description: 'Add a new document to the system',
      href: '/documents',
      icon: PlusIcon,
      color: 'bg-blue-500',
      requiresRole: UserRole.EDITOR,
    },
    {
      name: 'Ask Question',
      description: 'Get answers from your documents',
      href: '/qa',
      icon: QuestionMarkCircleIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Manage Users',
      description: 'View and manage system users',
      href: '/users',
      icon: UserGroupIcon,
      color: 'bg-purple-500',
      requiresRole: UserRole.ADMIN,
    },
  ].filter(action => !action.requiresRole || hasMinimumRole(action.requiresRole));

  const recentDocuments = documentsData?.documents || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.username}! Here's what's happening with your RAG FAQ system.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`flex-shrink-0 p-3 rounded-md ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {statsLoading ? '...' : stat.value.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.href}
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div className={`flex-shrink-0 p-2 rounded-md ${action.color}`}>
                  <action.icon className="h-5 w-5 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-gray-900">{action.name}</h3>
                  <p className="text-sm text-gray-500">{action.description}</p>
                </div>
                <ArrowRightIcon className="h-5 w-5 text-gray-400" />
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Documents */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Recent Documents</h2>
            <Link
              to="/documents"
              className="text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              View all
            </Link>
          </div>
          
          {documentsLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : recentDocuments.length > 0 ? (
            <div className="space-y-3">
              {recentDocuments.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{doc.original_filename}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(doc.created_at).toLocaleDateString()} • {doc.file_type}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      doc.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {doc.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No documents uploaded yet.</p>
              {hasMinimumRole(UserRole.EDITOR) && (
                <Link
                  to="/documents"
                  className="mt-2 inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  Upload your first document
                  <ArrowRightIcon className="ml-1 h-4 w-4" />
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 
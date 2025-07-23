import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { User, UserRole } from '../types';
import {
  UserGroupIcon,
  ShieldCheckIcon,
  UserIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';

const Users: React.FC = () => {
  const { user } = useAuth();

  // For now, we'll show a placeholder since the backend doesn't have a get all users endpoint
  // In a real implementation, you would fetch users from the API
  const mockUsers: User[] = [
    {
      id: 1,
      email: 'admin@example.com',
      username: 'admin',
      role: UserRole.ADMIN,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      email: 'editor@example.com',
      username: 'editor',
      role: UserRole.EDITOR,
      is_active: true,
      created_at: '2024-01-02T00:00:00Z',
    },
    {
      id: 3,
      email: 'viewer@example.com',
      username: 'viewer',
      role: UserRole.VIEWER,
      is_active: true,
      created_at: '2024-01-03T00:00:00Z',
    },
  ];

  const getRoleIcon = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return <ShieldCheckIcon className="h-5 w-5 text-red-500" />;
      case UserRole.EDITOR:
        return <EyeIcon className="h-5 w-5 text-blue-500" />;
      case UserRole.VIEWER:
        return <UserIcon className="h-5 w-5 text-green-500" />;
      default:
        return <UserIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getRoleBadgeColor = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'bg-red-100 text-red-800';
      case UserRole.EDITOR:
        return 'bg-blue-100 text-blue-800';
      case UserRole.VIEWER:
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <p className="mt-2 text-gray-600">
          Manage system users and their roles.
        </p>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900">System Users</h2>
          <div className="text-sm text-gray-500">
            Total: {mockUsers.length} users
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockUsers.map((userItem) => (
                <tr key={userItem.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center">
                          <span className="text-sm font-medium text-white">
                            {userItem.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {userItem.username}
                        </div>
                        <div className="text-sm text-gray-500">
                          {userItem.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getRoleIcon(userItem.role)}
                      <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(userItem.role)}`}>
                        {userItem.role}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      userItem.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {userItem.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(userItem.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-primary-600 hover:text-primary-900 mr-3">
                      Edit
                    </button>
                    <button className="text-red-600 hover:text-red-900">
                      Deactivate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Current User Info */}
        <div className="mt-8 p-4 bg-primary-50 rounded-lg">
          <h3 className="text-sm font-medium text-primary-900 mb-2">Current User</h3>
          <div className="flex items-center">
            <div className="flex-shrink-0 h-8 w-8">
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                <span className="text-xs font-medium text-white">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <div className="text-sm font-medium text-primary-900">
                {user?.username} (You)
              </div>
              <div className="text-sm text-primary-700">
                {user?.email} • {user?.role}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Role Information */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center mb-3">
            <ShieldCheckIcon className="h-6 w-6 text-red-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Admin</h3>
          </div>
          <p className="text-sm text-gray-600">
            Full system access. Can manage users, documents, and system settings.
          </p>
        </div>

        <div className="card">
          <div className="flex items-center mb-3">
            <EyeIcon className="h-6 w-6 text-blue-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Editor</h3>
          </div>
          <p className="text-sm text-gray-600">
            Can upload, manage documents, and ask questions. Cannot manage users.
          </p>
        </div>

        <div className="card">
          <div className="flex items-center mb-3">
            <UserIcon className="h-6 w-6 text-green-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Viewer</h3>
          </div>
          <p className="text-sm text-gray-600">
            Can view documents and ask questions. Cannot upload or manage content.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Users; 
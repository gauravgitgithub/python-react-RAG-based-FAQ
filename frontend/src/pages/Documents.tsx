import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { documentsAPI } from '../services/api';
import { Document, UserRole } from '../types';
import { toast } from 'react-hot-toast';
import {
  DocumentTextIcon,
  PlusIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  CloudArrowUpIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const Documents: React.FC = () => {
  const { hasMinimumRole } = useAuth();
  const queryClient = useQueryClient();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive'>('all');

  // Fetch documents
  const { data: documentsData, isLoading } = useQuery({
    queryKey: ['documents', filter],
    queryFn: () => documentsAPI.getDocuments({
      is_active: filter === 'all' ? undefined : filter === 'active',
    }),
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => documentsAPI.uploadDocument(file, setUploadProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['qa-stats'] });
      toast.success('Document uploaded successfully!');
      setShowUploadModal(false);
      setSelectedFile(null);
      setUploadProgress(0);
    },
    onError: () => {
      toast.error('Failed to upload document');
      setUploadProgress(0);
    },
  });

  // Toggle active mutation
  const toggleActiveMutation = useMutation({
    mutationFn: (id: number) => documentsAPI.toggleDocumentActive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['qa-stats'] });
      toast.success('Document status updated');
    },
    onError: () => {
      toast.error('Failed to update document status');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentsAPI.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['qa-stats'] });
      toast.success('Document deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete document');
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size must be less than 10MB');
        return;
      }
      if (!['.pdf', '.txt'].includes(file.name.toLowerCase().slice(file.name.lastIndexOf('.')))) {
        toast.error('Only PDF and TXT files are allowed');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    try {
      await uploadMutation.mutateAsync(selectedFile);
    } finally {
      setIsUploading(false);
    }
  };

  const handleToggleActive = (id: number) => {
    toggleActiveMutation.mutate(id);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id);
    }
  };

  const documents = documentsData?.documents || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="mt-2 text-gray-600">
            Manage your documents and control which ones are active for Q&A.
          </p>
        </div>
        
        {hasMinimumRole(UserRole.EDITOR) && (
          <button
            onClick={() => setShowUploadModal(true)}
            className="btn-primary inline-flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Upload Document
          </button>
        )}
      </div>

      {/* Filter */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'all'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            All Documents
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'active'
                ? 'bg-green-100 text-green-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilter('inactive')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'inactive'
                ? 'bg-gray-100 text-gray-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Inactive
          </button>
        </div>
      </div>

      {/* Documents List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      ) : documents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <div key={doc.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400 mr-3" />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {doc.original_filename}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
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
              
              <div className="mt-4 space-y-2">
                <div className="text-xs text-gray-500">
                  <span>Size: {(doc.file_size / 1024).toFixed(1)} KB</span>
                  <span className="mx-2">•</span>
                  <span>Type: {doc.file_type}</span>
                </div>
                
                <div className="flex space-x-2">
                  {hasMinimumRole(UserRole.EDITOR) && (
                    <>
                      <button
                        onClick={() => handleToggleActive(doc.id)}
                        disabled={toggleActiveMutation.isPending}
                        className="btn-secondary flex-1 text-xs py-1"
                      >
                        {doc.is_active ? (
                          <>
                            <EyeSlashIcon className="h-4 w-4 mr-1" />
                            Deactivate
                          </>
                        ) : (
                          <>
                            <EyeIcon className="h-4 w-4 mr-1" />
                            Activate
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        disabled={deleteMutation.isPending}
                        className="btn-danger text-xs py-1 px-2"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
          <p className="text-gray-500 mb-4">
            {filter === 'all'
              ? 'Get started by uploading your first document.'
              : `No ${filter} documents found.`}
          </p>
          {hasMinimumRole(UserRole.EDITOR) && (
            <button
              onClick={() => setShowUploadModal(true)}
              className="btn-primary inline-flex items-center"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Upload Document
            </button>
          )}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Document</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select File (PDF or TXT, max 10MB)
                </label>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={handleFileSelect}
                  className="input-field"
                />
                {selectedFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {selectedFile.name}
                  </p>
                )}
              </div>

              {isUploading && (
                <div className="mb-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Uploading... {uploadProgress}%
                  </p>
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || isUploading}
                  className="btn-primary flex-1"
                >
                  {isUploading ? 'Uploading...' : 'Upload'}
                </button>
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                    setUploadProgress(0);
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Documents; 
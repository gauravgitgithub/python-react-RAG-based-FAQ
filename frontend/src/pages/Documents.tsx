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

  // Upload mutation with enhanced error handling
  const uploadMutation = useMutation({
    mutationFn: (file: File) => documentsAPI.uploadDocument(file, setUploadProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['qa-stats'] });
      toast.success('Document uploaded and processed successfully!');
      setShowUploadModal(false);
      setSelectedFile(null);
      setUploadProgress(0);
    },
    onError: (error: any) => {
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error('Upload timed out. Please try with a smaller file or try again later.');
      } else if (error.response?.status === 408) {
        toast.error('Document processing timed out. Please try with a smaller file.');
      } else if (error.response?.data?.detail) {
        toast.error(`Upload failed: ${error.response.data.detail}`);
      } else {
        toast.error('Upload failed. Please try again.');
      }
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
    setUploadProgress(0);
    
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
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
        {hasMinimumRole(UserRole.EDITOR) && (
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <PlusIcon className="w-5 h-5" />
            Upload Document
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
        {[
          { key: 'all', label: 'All Documents' },
          { key: 'active', label: 'Active' },
          { key: 'inactive', label: 'Inactive' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key as any)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Documents List */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading documents...</p>
            </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
          <p className="mt-1 text-sm text-gray-500">
            {filter === 'all'
              ? 'Get started by uploading a document.'
              : `No ${filter} documents found.`}
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {documents.map((document) => (
              <li key={document.id}>
                <div className="px-4 py-4 flex items-center justify-between">
                <div className="flex items-center">
                    <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-900">
                        {document.original_filename}
                      </p>
                      <p className="text-sm text-gray-500">
                        {document.file_type.toUpperCase()} • {(document.file_size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                  <div className="flex items-center space-x-2">
                  {hasMinimumRole(UserRole.EDITOR) && (
                    <>
                      <button
                          onClick={() => handleToggleActive(document.id)}
                        disabled={toggleActiveMutation.isPending}
                          className={`p-2 rounded-md ${
                            document.is_active
                              ? 'text-green-600 hover:bg-green-50'
                              : 'text-gray-400 hover:bg-gray-50'
                          }`}
                          title={document.is_active ? 'Deactivate' : 'Activate'}
                      >
                          {document.is_active ? (
                            <EyeIcon className="h-5 w-5" />
                        ) : (
                            <EyeSlashIcon className="h-5 w-5" />
                        )}
                      </button>
                      <button
                          onClick={() => handleDelete(document.id)}
                        disabled={deleteMutation.isPending}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                          title="Delete"
                      >
                          <TrashIcon className="h-5 w-5" />
                      </button>
                    </>
                  )}
                </div>
              </div>
              </li>
          ))}
          </ul>
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
                  Select File
                </label>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>

                {selectedFile && (
                <div className="mb-4 p-3 bg-gray-50 rounded-md">
                  <p className="text-sm text-gray-700">
                    <strong>File:</strong> {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
              </div>
              )}

              {isUploading && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-700">Processing...</span>
                    <span className="text-sm text-gray-500">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    This may take a few minutes for large files...
                  </p>
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                    setUploadProgress(0);
                  }}
                  disabled={isUploading}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || isUploading}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 flex items-center gap-2"
                >
                  {isUploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <CloudArrowUpIcon className="h-4 w-4" />
                      Upload
                    </>
                  )}
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
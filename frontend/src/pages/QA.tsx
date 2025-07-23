import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { qaAPI, documentsAPI } from '../services/api';
import { QuestionRequest, AnswerResponse, SourceChunk } from '../types';
import { toast } from 'react-hot-toast';
import {
  QuestionMarkCircleIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline';

const QA: React.FC = () => {
  const { hasMinimumRole } = useAuth();
  const { UserRole } = require('../types');
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(5);

  // Fetch active documents for context
  const { data: documentsData } = useQuery({
    queryKey: ['documents', 'active'],
    queryFn: () => documentsAPI.getDocuments({ is_active: true }),
  });

  // Ask question mutation
  const askMutation = useMutation({
    mutationFn: (request: QuestionRequest) => qaAPI.askQuestion(request),
    onError: () => {
      toast.error('Failed to get answer. Please try again.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }

    const request: QuestionRequest = {
      question: question.trim(),
      top_k: topK,
    };

    askMutation.mutate(request);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const activeDocuments = documentsData?.documents || [];
  const hasActiveDocuments = activeDocuments.length > 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Ask a Question</h1>
        <p className="mt-2 text-gray-600">
          Get intelligent answers from your documents using AI-powered search.
        </p>
      </div>

      {/* Question Form */}
      <div className="card mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything about your documents..."
              className="input-field h-32 resize-none"
              disabled={askMutation.isPending}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <label htmlFor="topK" className="text-sm font-medium text-gray-700">
                Number of sources:
              </label>
              <select
                id="topK"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="input-field w-20"
                disabled={askMutation.isPending}
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={askMutation.isPending || !question.trim()}
              className="btn-primary inline-flex items-center"
            >
              {askMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Thinking...
                </>
              ) : (
                <>
                  <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                  Ask Question
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Active Documents Info */}
      {!hasActiveDocuments && hasMinimumRole(UserRole.EDITOR) && (
        <div className="card mb-8 bg-yellow-50 border-yellow-200">
          <div className="flex items-center">
            <DocumentTextIcon className="h-5 w-5 text-yellow-600 mr-2" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800">No Active Documents</h3>
              <p className="text-sm text-yellow-700">
                You need to upload and activate documents before you can ask questions.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Answer Display */}
      {askMutation.data && (
        <div className="space-y-6">
          {/* Answer */}
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Answer</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-800 whitespace-pre-wrap">{askMutation.data.answer}</p>
              <button
                onClick={() => copyToClipboard(askMutation.data.answer)}
                className="mt-3 inline-flex items-center text-sm text-primary-600 hover:text-primary-500"
              >
                <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                Copy answer
              </button>
            </div>
          </div>

          {/* Sources */}
          {askMutation.data.sources.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Sources ({askMutation.data.sources.length})
              </h2>
              <div className="space-y-4">
                {askMutation.data.sources.map((source, index) => (
                  <SourceCard key={index} source={source} index={index + 1} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error State */}
      {askMutation.isError && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center">
            <QuestionMarkCircleIcon className="h-5 w-5 text-red-600 mr-2" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700">
                Failed to get an answer. Please check your question and try again.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface SourceCardProps {
  source: SourceChunk;
  index: number;
}

const SourceCard: React.FC<SourceCardProps> = ({ source, index }) => {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Source copied to clipboard!');
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center">
          <span className="inline-flex items-center justify-center w-6 h-6 bg-primary-100 text-primary-800 text-xs font-medium rounded-full mr-3">
            {index}
          </span>
          <div>
            <h4 className="text-sm font-medium text-gray-900">
              {source.document_name}
            </h4>
            <p className="text-xs text-gray-500">
              Chunk {source.chunk_index} • Similarity: {(source.similarity_score * 100).toFixed(1)}%
            </p>
          </div>
        </div>
        <button
          onClick={() => copyToClipboard(source.content)}
          className="text-gray-400 hover:text-gray-600"
        >
          <ClipboardDocumentIcon className="h-4 w-4" />
        </button>
      </div>
      <div className="bg-gray-50 rounded p-3">
        <p className="text-sm text-gray-700 leading-relaxed">{source.content}</p>
      </div>
    </div>
  );
};

export default QA; 
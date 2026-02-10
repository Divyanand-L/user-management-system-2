import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';
import Button from '../components/ui/Button';
import { getImageUrl } from '../utils/imageHelper';
import Toast from '../components/ui/Toast';

const AdminPanel = () => {
  const navigate = useNavigate();
  const { logout, refreshUserData } = useAuth();
  
  // State management
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [actionLoading, setActionLoading] = useState({});
  
  // Pagination state
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalUsers: 0,
    limit: 10,
    hasNextPage: false,
    hasPrevPage: false
  });

  // Fetch users - wrapped in useCallback to prevent recreating on every render
  const fetchUsers = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: pagination.limit,
      };

      const response = await api.get('/users', { params });
      
      // Backend returns: { data: [...users], pagination: {...} }
      setUsers(response.data.data || []);
      setPagination({
        currentPage: response.data.pagination?.page || 1,
        totalPages: response.data.pagination?.pages || 1,
        totalUsers: response.data.pagination?.total || 0,
        limit: response.data.pagination?.limit || 10,
        hasNextPage: response.data.pagination?.page < response.data.pagination?.pages,
        hasPrevPage: response.data.pagination?.page > 1
      });
    } catch (err) {
      console.error('Fetch users error:', err);
      setToast({ 
        type: 'error', 
        message: err.response?.data?.message || err.response?.data?.error?.message || 'Failed to fetch users' 
      });
    } finally {
      setLoading(false);
    }
  }, [pagination.limit]);

  // Initial load - only once on mount
  useEffect(() => {
    let mounted = true;
    
    const loadData = async () => {
      if (mounted && refreshUserData) {
        await refreshUserData();
      }
      if (mounted) {
        await fetchUsers(1);
      }
    };
    
    loadData();
    
    return () => {
      mounted = false;
    };
  }, []); // Empty dependency array - only run once

  // Refetch when returning to this page
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchUsers(pagination.currentPage || 1);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchUsers, pagination.currentPage]);

  // Handle pagination
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      fetchUsers(newPage);
    }
  };

  // Handle role change (promote/demote)
  const handleRoleChange = async (userId, action) => {
    try {
      setActionLoading(prev => ({ ...prev, [userId]: true }));
      
      const newRole = action === 'promote' ? 'admin' : 'user';
      
      await api.patch(`/users/${userId}/role`, {
        role: newRole
      });
      
      // Update user in local state without refetching
      setUsers(prev => prev.map(user => 
        user._id === userId 
          ? { ...user, role: newRole }
          : user
      ));
      
      setToast({ 
        type: 'success', 
        message: `User ${action === 'promote' ? 'promoted to' : 'demoted from'} admin` 
      });
    } catch (err) {
      setToast({ 
        type: 'error', 
        message: err.response?.data?.error?.message || 'Action failed' 
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [userId]: false }));
    }
  };

  // Handle delete user
  const handleDelete = async (userId) => {
    try {
      setActionLoading(prev => ({ ...prev, [userId]: true }));
      await api.delete(`/users/${userId}`);
      
      // Remove user from local state
      setUsers(prev => prev.filter(user => user._id !== userId));
      setPagination(prev => ({ ...prev, totalUsers: prev.totalUsers - 1 }));
      
      setToast({ type: 'success', message: 'User deleted successfully' });
      setDeleteConfirm(null);
    } catch (err) {
      setToast({ 
        type: 'error', 
        message: err.response?.data?.error?.message || 'Failed to delete user' 
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [userId]: false }));
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              User Management System - Admin Panel
            </h1>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={() => navigate('/profile')}>
                My Profile
              </Button>
              <Button variant="danger" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Users Table */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              All Users <span className="text-sm font-normal text-gray-500">({pagination.totalUsers} total)</span>
            </h2>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No users found</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contact
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Location
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr 
                        key={user._id} 
                        className="hover:bg-gray-50 transition-colors cursor-pointer"
                        onClick={() => navigate(`/admin/user/${user._id}`)}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-3">
                            {user.profile_image ? (
                              <img
                                src={getImageUrl(user.profile_image)}
                                alt={user.name}
                                className="w-10 h-10 rounded-full object-cover"
                              />
                            ) : (
                              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-100 to-indigo-100 flex items-center justify-center">
                                <span className="text-sm font-bold text-blue-600">
                                  {user.name?.charAt(0).toUpperCase()}
                                </span>
                              </div>
                            )}
                            <div>
                              <p className="text-sm font-medium text-gray-900">{user.name}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-900">{user.email}</p>
                          {user.phone && (
                            <p className="text-xs text-gray-500">{user.phone}</p>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-900">
                            {user.city || 'N/A'}, {user.state || 'N/A'}
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold capitalize ${
                            user.role === 'admin' 
                              ? 'bg-purple-100 text-purple-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex justify-center items-center gap-2" onClick={(e) => e.stopPropagation()}>
                            {user.role === 'admin' ? (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRoleChange(user._id, 'demote');
                                }}
                                disabled={actionLoading[user._id]}
                                className="px-3 py-1.5 text-xs font-medium text-orange-700 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-orange-200"
                              >
                                {actionLoading[user._id] ? 'Loading...' : 'Dismiss Admin'}
                              </button>
                            ) : (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRoleChange(user._id, 'promote');
                                }}
                                disabled={actionLoading[user._id]}
                                className="px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-green-200"
                              >
                                {actionLoading[user._id] ? 'Loading...' : 'Make Admin'}
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setDeleteConfirm(user._id);
                              }}
                              disabled={actionLoading[user._id]}
                              className="px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-red-200"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {pagination.totalPages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    Page {pagination.currentPage} of {pagination.totalPages}
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(pagination.currentPage - 1)}
                      disabled={!pagination.hasPrevPage}
                    >
                      Previous
                    </Button>
                    
                    {/* Page numbers */}
                    {[...Array(pagination.totalPages)].map((_, i) => {
                      const pageNum = i + 1;
                      // Show first 2, last 2, and current page with neighbors
                      if (
                        pageNum === 1 ||
                        pageNum === pagination.totalPages ||
                        Math.abs(pageNum - pagination.currentPage) <= 1
                      ) {
                        return (
                          <button
                            key={pageNum}
                            onClick={() => handlePageChange(pageNum)}
                            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                              pagination.currentPage === pageNum
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {pageNum}
                          </button>
                        );
                      } else if (
                        pageNum === 2 && pagination.currentPage > 3 ||
                        pageNum === pagination.totalPages - 1 && pagination.currentPage < pagination.totalPages - 2
                      ) {
                        return <span key={pageNum} className="px-2">...</span>;
                      }
                      return null;
                    })}
                    
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(pagination.currentPage + 1)}
                      disabled={!pagination.hasNextPage}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Confirm Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this user? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-4">
              <Button
                variant="outline"
                onClick={() => setDeleteConfirm(null)}
                disabled={actionLoading[deleteConfirm]}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => handleDelete(deleteConfirm)}
                loading={actionLoading[deleteConfirm]}
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;

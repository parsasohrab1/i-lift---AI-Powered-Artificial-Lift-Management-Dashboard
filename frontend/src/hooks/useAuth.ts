'use client'

import { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { apiClient } from '@/lib/api'
import toast from 'react-hot-toast'

interface User {
  user_id: string
  username: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  })

  const queryClient = useQueryClient()

  // Load auth state from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        setAuthState({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        })
      } catch (e) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        setAuthState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })
      }
    } else {
      setAuthState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      })
    }
  }, [])

  // Fetch current user
  const { data: currentUser } = useQuery(
    ['user', 'me'],
    async () => {
      const response = await apiClient.get('/auth/me')
      return response.data
    },
    {
      enabled: authState.isAuthenticated,
      onSuccess: (data) => {
        setAuthState((prev) => ({
          ...prev,
          user: data,
        }))
        localStorage.setItem('user', JSON.stringify(data))
      },
      onError: () => {
        logout()
      },
    }
  )

  const loginMutation = useMutation(
    async ({ username, password }: { username: string; password: string }) => {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      return response.data
    },
    {
      onSuccess: async (data) => {
        const { access_token, refresh_token } = data

        localStorage.setItem('token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        // Fetch user info
        const userResponse = await apiClient.get('/auth/me')
        const user = userResponse.data

        localStorage.setItem('user', JSON.stringify(user))

        setAuthState({
          user,
          token: access_token,
          isAuthenticated: true,
          isLoading: false,
        })

        toast.success('Login successful')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Login failed')
        throw error
      },
    }
  )

  const logoutMutation = useMutation(
    async () => {
      await apiClient.post('/auth/logout')
    },
    {
      onSuccess: () => {
        logout()
        toast.success('Logged out successfully')
      },
      onError: () => {
        logout()
      },
    }
  )

  const login = useCallback(
    async (username: string, password: string) => {
      await loginMutation.mutateAsync({ username, password })
    },
    [loginMutation]
  )

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    })
    queryClient.clear()
  }, [queryClient])

  const handleLogout = useCallback(async () => {
    try {
      await logoutMutation.mutateAsync()
    } catch {
      logout()
    }
  }, [logoutMutation, logout])

  return {
    user: authState.user || currentUser,
    token: authState.token,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading || loginMutation.isLoading,
    login,
    logout: handleLogout,
  }
}


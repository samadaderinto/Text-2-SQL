import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import ProtectedRoute, { decryptJWT, encryptJWT } from '../utils/hooks'

describe('ProtectedRoute', () => {
  it('redirects unauthenticated users to sign in', () => {
    render(
      <MemoryRouter
        initialEntries={['/dashboard']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <h1>Dashboard</h1>
              </ProtectedRoute>
            }
          />
          <Route path="/auth/signin" element={<h1>Sign in</h1>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Dashboard' })).not.toBeInTheDocument()
  })

  it('renders protected content when an access token exists', () => {
    localStorage.setItem('access', 'encrypted-access-token')

    render(
      <MemoryRouter
        initialEntries={['/dashboard']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <h1>Dashboard</h1>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })
})

describe('JWT storage helpers', () => {
  it('encrypts and decrypts a token with the configured key', () => {
    const token = 'test-access-token'
    const key = 'test-only-secret'

    expect(decryptJWT(encryptJWT(token, key), key)).toBe(token)
  })
})

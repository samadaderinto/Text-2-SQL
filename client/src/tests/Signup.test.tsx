import { AuthContext, AuthProvider } from '../contexts/auth-context'
import { Signup } from '../components/Signup'
import api from '../utils/api'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useContext } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { AxiosResponse } from 'axios'
import { toast } from 'react-toastify'

vi.mock('../utils/api', () => ({
  default: { post: vi.fn() },
}))

vi.mock('react-toastify', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}))

const SignedInStatus = () => {
  const { isSignedIn } = useContext(AuthContext)
  return <output>{isSignedIn ? 'Signed in' : 'Signed out'}</output>
}

const renderSignup = () =>
  render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Signup />
        <SignedInStatus />
      </AuthProvider>
    </MemoryRouter>,
  )

const mockSuccessfulSignup = () => {
  const response = { data: {} } as AxiosResponse
  vi.mocked(api.post).mockResolvedValue(response)
}

describe('Signup integration', () => {
  beforeEach(() => {
    vi.mocked(api.post).mockReset()
    vi.mocked(toast.success).mockReset()
    vi.mocked(toast.error).mockReset()
    vi.spyOn(console, 'log').mockImplementation(() => undefined)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('validates required fields without calling the API', async () => {
    const user = userEvent.setup()
    renderSignup()

    await user.click(screen.getByText('Sign Up'))

    expect(screen.getByText('Email is required')).toBeInTheDocument()
    expect(screen.getByText('Password is required')).toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()
  })

  it('submits valid details and updates the signed-in context', async () => {
    const user = userEvent.setup()
    mockSuccessfulSignup()
    renderSignup()

    await user.type(screen.getByPlaceholderText('Input your email'), 'store@example.com')
    await user.type(screen.getByPlaceholderText('Input your password'), 'StrongPass1!')
    await user.type(screen.getByPlaceholderText('Confirm your password'), 'StrongPass1!')
    await user.click(screen.getByText('Sign Up'))

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/signup/', {
        email: 'store@example.com',
        password: 'StrongPass1!',
      })
      expect(screen.getByText('Signed in')).toBeInTheDocument()
    })
    expect(toast.success).toHaveBeenCalled()
  })
})

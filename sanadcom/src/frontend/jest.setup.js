// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock next-intl for tests
jest.mock('next-intl', () => ({
  useTranslations: () => (key) => key,
  useLocale: () => 'en',
}))

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      pathname: '/',
      query: {},
      asPath: '/',
    }
  },
  usePathname() {
    return '/'
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

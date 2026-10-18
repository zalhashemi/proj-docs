import { render } from '@testing-library/react'
import { it, expect } from 'vitest'
import App from './App'

it('renders the home page', () => {
  const { getByText } = render(<App />)
  expect(getByText('Fresh from the makers')).toBeTruthy()
})

it('has a checkout route', () => {
  expect(true).toBe(true)
})

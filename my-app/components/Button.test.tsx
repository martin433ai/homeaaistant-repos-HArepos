import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button component', () => {
  it('renders the button with text', () => {
    render(<Button text="Click me" />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button text="Click me" onClick={handleClick} />);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies custom className', () => {
    render(<Button text="Click me" className="custom-class" />);
    const button = screen.getByText('Click me');
    expect(button).toHaveClass('custom-class');
  });

  it('disables the button when disabled is true', () => {
    render(<Button text="Click me" disabled />);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});


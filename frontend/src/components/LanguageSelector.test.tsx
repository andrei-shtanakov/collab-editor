import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageSelector } from './LanguageSelector';

describe('LanguageSelector', () => {
  it('renders with the current language selected', () => {
    render(
      <LanguageSelector
        value="python"
        onChange={() => {}}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('python');
  });

  it('displays all supported languages', () => {
    render(
      <LanguageSelector
        value="python"
        onChange={() => {}}
      />
    );

    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(10); // 10 languages

    const languages = options.map((opt) => opt.textContent);
    expect(languages).toContain('Python');
    expect(languages).toContain('JavaScript');
    expect(languages).toContain('TypeScript');
  });

  it('calls onChange when selection changes', () => {
    const handleChange = vi.fn();
    render(
      <LanguageSelector
        value="python"
        onChange={handleChange}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'javascript' } });

    expect(handleChange).toHaveBeenCalledWith('javascript');
  });

  it('is disabled when disabled prop is true', () => {
    render(
      <LanguageSelector
        value="python"
        onChange={() => {}}
        disabled={true}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });
});

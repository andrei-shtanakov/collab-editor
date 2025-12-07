/**
 * Language selector dropdown
 */

import type { ProgrammingLanguage } from '../types';
import { LANGUAGE_LABELS } from '../types';

interface LanguageSelectorProps {
  value: ProgrammingLanguage;
  onChange: (language: ProgrammingLanguage) => void;
  disabled?: boolean;
}

const LANGUAGES: ProgrammingLanguage[] = [
  'python',
  'javascript',
  'typescript',
  'java',
  'cpp',
  'go',
  'rust',
  'ruby',
  'php',
  'sql',
];

export function LanguageSelector({
  value,
  onChange,
  disabled = false,
}: LanguageSelectorProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as ProgrammingLanguage)}
      disabled={disabled}
      className="px-3 py-1.5 bg-gray-700 text-white rounded border border-gray-600 
                 focus:outline-none focus:border-blue-500 text-sm
                 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {LANGUAGES.map((lang) => (
        <option key={lang} value={lang}>
          {LANGUAGE_LABELS[lang]}
        </option>
      ))}
    </select>
  );
}

/**
 * API types matching OpenAPI specification
 */

export type ProgrammingLanguage = 
  | 'python'
  | 'javascript'
  | 'typescript'
  | 'java'
  | 'cpp'
  | 'go'
  | 'rust'
  | 'ruby'
  | 'php'
  | 'sql';

export type SessionStatus = 'active' | 'idle' | 'closed';

export interface Session {
  id: string;
  url: string;
  websocket_url: string;
  language: ProgrammingLanguage;
  title: string | null;
  created_at: string;
  status: SessionStatus;
  participants_count: number;
}

export interface CreateSessionRequest {
  language?: ProgrammingLanguage;
  initial_code?: string;
  title?: string;
}

export interface ExecuteResult {
  success: boolean;
  output: string;
  stderr?: string;
  execution_time_ms?: number;
  error?: string;
  error_type?: string;
}

// Monaco language mappings
export const LANGUAGE_MAP: Record<ProgrammingLanguage, string> = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  java: 'java',
  cpp: 'cpp',
  go: 'go',
  rust: 'rust',
  ruby: 'ruby',
  php: 'php',
  sql: 'sql',
};

export const LANGUAGE_LABELS: Record<ProgrammingLanguage, string> = {
  python: 'Python',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  java: 'Java',
  cpp: 'C++',
  go: 'Go',
  rust: 'Rust',
  ruby: 'Ruby',
  php: 'PHP',
  sql: 'SQL',
};

// Default code templates
export const DEFAULT_CODE: Record<ProgrammingLanguage, string> = {
  python: `# Python Code
def hello(name: str) -> str:
    return f"Hello, {name}!"

print(hello("World"))
`,
  javascript: `// JavaScript Code
function hello(name) {
    return \`Hello, \${name}!\`;
}

console.log(hello("World"));
`,
  typescript: `// TypeScript Code
function hello(name: string): string {
    return \`Hello, \${name}!\`;
}

console.log(hello("World"));
`,
  java: `// Java Code
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
`,
  cpp: `// C++ Code
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
`,
  go: `// Go Code
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
`,
  rust: `// Rust Code
fn main() {
    println!("Hello, World!");
}
`,
  ruby: `# Ruby Code
def hello(name)
  "Hello, #{name}!"
end

puts hello("World")
`,
  php: `<?php
// PHP Code
function hello($name) {
    return "Hello, $name!";
}

echo hello("World");
`,
  sql: `-- SQL Code
SELECT 'Hello, World!' AS greeting;
`,
};

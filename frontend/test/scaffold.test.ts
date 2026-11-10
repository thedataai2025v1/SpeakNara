import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Frontend Scaffold', () => {
  const frontendDir = process.cwd();
  
  it('has required configuration files', () => {
    const requiredFiles = [
      'package.json',
      'tsconfig.json', 
      'next.config.mjs',
      'tailwind.config.js',
      'postcss.config.js',
      'components.json'
    ];
    
    requiredFiles.forEach(file => {
      const filePath = path.join(frontendDir, file);
      expect(fs.existsSync(filePath)).toBe(true);
    });
  });
  
  it('has app directory structure', () => {
    const appDir = path.join(frontendDir, 'src/app');
    expect(fs.existsSync(appDir)).toBe(true);
    
    const files = fs.readdirSync(appDir);
    expect(files).toContain('layout.tsx');
    expect(files).toContain('page.tsx');
  });
  
  it('has login and register pages', () => {
    const loginPath = path.join(frontendDir, 'src/app/login/page.tsx');
    const registerPath = path.join(frontendDir, 'src/app/register/page.tsx');
    
    expect(fs.existsSync(loginPath)).toBe(true);
    expect(fs.existsSync(registerPath)).toBe(true);
  });
  
  it('has supabase client', () => {
    const clientPath = path.join(frontendDir, 'src/utils/supabase/client.ts');
    expect(fs.existsSync(clientPath)).toBe(true);
  });
});

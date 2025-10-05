/**
 * Simple logger factory used across the app.
 * Usage:
 *   import logger from './utils/logger';
 *   const log = logger('MyModule.jsx');
 *   log.info('something happened', { some: 'data' });
 */
export default function logger(moduleName = 'unknown') {
  const ts = () => new Date().toISOString();
  interface ConsoleMethod {
    (...args: any[]): void;
  }

  function safeConsoleMethod(method: keyof Console, args: any[]): void {
    if (typeof console === 'undefined') return;
    const prefixed = [`[${ts()}] [${moduleName}]`, ...args];
    if (typeof console[method] === 'function') {
      (console[method] as ConsoleMethod).apply(console, prefixed);
    } else {
      console.log.apply(console, prefixed);
    }
  }
  return {
    debug: (...args: unknown[]) => safeConsoleMethod('debug', args),
    info: (...args: unknown[]) => safeConsoleMethod('info', args),
    warn: (...args: unknown[]) => safeConsoleMethod('warn', args),
    error: (...args: unknown[]) => safeConsoleMethod('error', args),
  };
}

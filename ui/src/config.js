// Environment variables are automatically loaded by Vite
const mode = import.meta.env.MODE || 'development';
console.log('Current Environment Mode:', mode);

export const config = {
  environment: mode,
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
  apiUrl: import.meta.env.VITE_API_URL,
  // Add other config variables as needed
};

// Log the config (excluding sensitive data)
console.log('Environment Config:', {
  environment: config.environment,
  apiUrl: config.apiUrl,
  // Don't log sensitive keys
}); 
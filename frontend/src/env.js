// Allows for env vars set via .env file (local) or injected at run time (deployed)
export const env = {
    ...import.meta.env,
    ...window?.config || {},
  };

// Only env files for build

export const buildEnv = {
    CLIENT_URL: import.meta.env?.CLIENT_URL ?? "http://localhost:5173"
};

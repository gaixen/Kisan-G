import React, { useState } from 'react';
import AuthForm from './AuthForm';
import { useAuth } from '../../src/hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false), [error, setError] = useState<string | undefined>();

    const handleSubmit = async ({ email, password }: { email: string; password: string; }) => {
        setLoading(true); setError(undefined);
        try { await login(email, password); navigate("/"); }
        catch { setError("Login failed. Check credentials."); }
        setLoading(false);
    };

    return <AuthForm onSubmit={handleSubmit} loading={loading} error={error} />;
};
export default Login;

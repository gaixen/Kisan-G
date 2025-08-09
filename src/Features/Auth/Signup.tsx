import React, { useState } from 'react';
import AuthForm from './AuthForm';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
    const { signup } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false), [error, setError] = useState<string | undefined>();

    const handleSubmit = async ({ name, email, password }: {name?: string; email: string; password: string; }) => {
        setLoading(true); setError(undefined);
        try { await signup(name || "", email, password); navigate("/"); }
        catch { setError("Signup failed. Try again."); }
        setLoading(false);
    };

    return <AuthForm onSubmit={handleSubmit} loading={loading} error={error} isSignup />;
};
export default Signup;

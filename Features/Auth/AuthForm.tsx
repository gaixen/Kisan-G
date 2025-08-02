import React, { useState } from 'react';

type Props = {
    isSignup?: boolean;
    onSubmit: (fields: {name?: string, email: string, password: string}) => void;
    loading?: boolean;
    error?: string;
};
const AuthForm: React.FC<Props> = ({ isSignup = false, onSubmit, loading, error }) => {
    const [fields, setFields] = useState({ name: "", email: "", password: "" });
    return (
        <form className="max-w-sm mx-auto bg-white shadow rounded p-6 mt-16"
        onSubmit={e => { e.preventDefault(); onSubmit(fields); }}>
        <h2 className="text-2xl font-bold mb-4">{isSignup ? "Sign Up" : "Log In"}</h2>
        {isSignup && (
            <input className="mb-2 p-2 w-full border rounded"
            type="text" placeholder="Name" required
            value={fields.name} onChange={e => setFields(f => ({...f, name: e.target.value}))} />
        )}
        <input className="mb-2 p-2 w-full border rounded"
            type="email" placeholder="Email" required
            value={fields.email} onChange={e => setFields(f => ({...f, email: e.target.value}))} />
        <input className="mb-2 p-2 w-full border rounded"
            type="password" placeholder="Password" required
            value={fields.password} onChange={e => setFields(f => ({...f, password: e.target.value}))} />
            {error && <div className="text-red-600 mb-2">{error}</div>}
        <button className="bg-primary px-4 py-2 rounded text-white w-full font-bold mb-2" disabled={loading}>
            {isSignup ? "Sign Up" : "Log In"}
        </button>
        </form>
    );
};
export default AuthForm;

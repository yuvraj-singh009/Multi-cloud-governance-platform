
import { useState } from "react";

import { supabase } from "../services/supabase";

export default function Login() {

    const [isSignup, setIsSignup] = useState(false);

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    const [name, setName] = useState("");

    const [error, setError] = useState("");

    const [loading, setLoading] = useState(false);


    async function handleSubmit(e) {

        e.preventDefault();

        setError("");
        setLoading(true);

        try {

            if (isSignup) {

                const { error } =
                    await supabase.auth.signUp({

                        email,
                        password,

                        options: {
                            data: {
                                full_name: name
                            }
                        }

                    });

                if (error) throw error;

                setError(
                    "Registration successful. Check your email if confirmation is enabled."
                );

            } else {

                const { error } =
                    await supabase.auth.signInWithPassword({

                        email,
                        password

                    });

                if (error) throw error;

            }

        } catch (err) {

            setError(err.message);

        } finally {

            setLoading(false);

        }

    }


    return (

        <div className="auth-page">

            <div className="auth-card">

                <h1>CloudGuard</h1>

                <p>
                    Cloud Cost & Resource Governance Platform
                </p>

                <h2>
                    {isSignup ? "Create Account" : "Welcome Back"}
                </h2>

                <form onSubmit={handleSubmit}>

                    {isSignup && (

                        <input
                            placeholder="Full Name"
                            value={name}
                            onChange={e =>
                                setName(e.target.value)
                            }
                            required
                        />

                    )}

                    <input
                        type="email"
                        placeholder="Email Address"
                        value={email}
                        onChange={e =>
                            setEmail(e.target.value)
                        }
                        required
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={e =>
                            setPassword(e.target.value)
                        }
                        required
                    />

                    <button
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Please wait..."
                            : isSignup
                                ? "Create Account"
                                : "Login"
                        }
                    </button>

                </form>

                {error && (
                    <p className="error-message">
                        {error}
                    </p>
                )}

                <p>
                    {isSignup
                        ? "Already have an account?"
                        : "Don't have an account?"
                    }

                    <button
                        className="text-button"
                        onClick={() => {
                            setIsSignup(!isSignup);
                            setError("");
                        }}
                    >
                        {isSignup ? "Login" : "Sign Up"}
                    </button>

                </p>

            </div>

        </div>

    );

}

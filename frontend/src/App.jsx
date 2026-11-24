import { useEffect, useState } from "react";

import { supabase } from "./services/supabase";

import Login from "./pages/Login";

import Dashboard from "./pages/Dashboard";


export default function App() {

    const [session, setSession] = useState(null);

    const [loading, setLoading] = useState(true);


    useEffect(() => {

        supabase.auth.getSession().then(({ data }) => {

            setSession(data.session);

            setLoading(false);

        });


        const {
            data: { subscription }
        } = supabase.auth.onAuthStateChange(
            (_event, session) => {

                setSession(session);

                setLoading(false);

            }
        );


        return () => subscription.unsubscribe();

    }, []);


    if (loading) {

        return <div className="loading">Loading...</div>;

    }


    return (

        session
            ? <Dashboard session={session} />
            : <Login />

    );

}
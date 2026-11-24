
import { useEffect, useState } from "react";

import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

import { supabase } from "../services/supabase";

import { startCloudScan } from "../services/api";


export default function Dashboard({ session }) {

    const [accounts, setAccounts] = useState([]);

    const [selectedAccount, setSelectedAccount] = useState("");

    const [resources, setResources] = useState([]);

    const [violations, setViolations] = useState([]);

    const [scans, setScans] = useState([]);

    const [totalSavings, setTotalSavings] = useState(0);

    const [loading, setLoading] = useState(true);

    const [accountsLoading, setAccountsLoading] = useState(true);

    const [scanning, setScanning] = useState(false);

    const [error, setError] = useState("");

    const [accountName, setAccountName] = useState("");


    async function loadAccounts() {
        try {
            const { data, error } = await supabase
                .from("cloud_accounts")
                .select("*")
                .eq("user_id", session.user.id)
                .order("created_at", {
                    ascending: false
                });

            if (error) throw error;

            const accountData = data || [];

            setAccounts(accountData);

            if (accountData.length > 0) {
                setSelectedAccount(accountData[0].id);
            }

        } catch (err) {
            console.error("Account loading error:", err);
            setError(err.message);

        } finally {
            setAccountsLoading(false);
        }
    }


    async function loadDashboard(accountId) {

        setLoading(true);

        setError("");

        try {

            const { data: scanData, error: scanError } =
                await supabase

                    .from("scan_jobs")

                    .select("*")

                    .eq("account_id", accountId)

                    .order("created_at", {
                        ascending: false
                    });

            if (scanError) throw scanError;

            setScans(scanData);

            const latestScan = scanData.find(
                scan => scan.status === "completed"
            );

            if (!latestScan) {

                setResources([]);
                setViolations([]);
                setTotalSavings(0);

                return;

            }

            const { data: resourceData, error: resourceError } =
                await supabase

                    .from("resource_snapshots")

                    .select("*")

                    .eq("scan_id", latestScan.id);

            if (resourceError) throw resourceError;

            setResources(resourceData);

            const { data: violationData, error: violationError } =
                await supabase

                    .from("policy_violations")

                    .select("*")

                    .eq("scan_id", latestScan.id);

            if (violationError) throw violationError;

            setViolations(violationData);

            const { data: costData, error: costError } =
                await supabase

                    .from("cost_estimates")

                    .select("estimated_monthly_waste")

                    .eq("scan_id", latestScan.id);

            if (costError) throw costError;

            const savings = costData.reduce(
                (total, item) =>
                    total + Number(
                        item.estimated_monthly_waste || 0
                    ),
                0
            );

            setTotalSavings(savings);

        } catch (err) {

            setError(err.message);

        } finally {

            setLoading(false);

        }

    }


    async function createAccount(e) {

        e.preventDefault();

        setError("");

        try {

            const { data, error } = await supabase

                .from("cloud_accounts")

                .insert({

                    user_id: session.user.id,

                    account_name: accountName,

                    provider: "AWS",

                    account_identifier: "000000000000",

                    region: "ap-south-1",

                    connection_type: "localstack"

                })

                .select()

                .single();

            if (error) throw error;

            setAccounts(old => [data, ...old]);

            setSelectedAccount(data.id);

            setAccountName("");

        } catch (err) {

            setError(err.message);

        }

    }


    async function handleScan() {

        if (!selectedAccount) return;

        setScanning(true);

        setError("");

        try {

            const result = await startCloudScan(
                selectedAccount,
                session.access_token
            );

            await loadDashboard(selectedAccount);

            console.log("FULL SCAN RESULT:", result);

            alert(
                `Resources discovered: ${result.total_resources}\n\n` +
                `Scanner errors: ${JSON.stringify(result.errors, null, 2)}`
            );

        } catch (err) {

            setError(
                err.response?.data?.detail || err.message
            );

        } finally {

            setScanning(false);

        }

    }


    useEffect(() => {
        if (session?.user?.id) {
            loadAccounts();
        }
    }, [session?.user?.id]);


    useEffect(() => {

        if (selectedAccount) {

            loadDashboard(selectedAccount);

        }

    }, [selectedAccount]);


    const resourceCounts = Object.entries(

        resources.reduce((acc, item) => {

            acc[item.resource_type] =
                (acc[item.resource_type] || 0) + 1;

            return acc;

        }, {})

    ).map(([name, total]) => ({

        name,
        total

    }));


    const criticalCount = violations.filter(
        item => item.severity === "critical"
    ).length;


    const activeCount = resources.filter(
        item => ["running", "available", "active", "associated"]
            .includes(item.resource_state)
    ).length;


    if (accountsLoading || (loading && selectedAccount)) {
        return (
            <div className="loading">
                Loading dashboard...
            </div>
        );
    }


    return (

        <div className="dashboard">

            <header className="topbar">

                <div>

                    <h1>Cloud Governance</h1>

                    <p>
                        Cost optimization and security monitoring
                    </p>

                </div>

                <button
                    onClick={() => supabase.auth.signOut()}
                    className="logout-button"
                >
                    Logout
                </button>

            </header>


            {error && (
                <p className="error-message">{error}</p>
            )}


            <section className="account-section">

                <select
                    value={selectedAccount}
                    onChange={e =>
                        setSelectedAccount(e.target.value)
                    }
                >

                    {accounts.map(account => (

                        <option
                            key={account.id}
                            value={account.id}
                        >
                            {account.account_name}
                        </option>

                    ))}

                </select>


                <button
                    onClick={handleScan}
                    disabled={!selectedAccount || scanning}
                >

                    {scanning ? "Scanning..." : "Start Cloud Scan"}

                </button>

            </section>


            {accounts.length === 0 && (

                <form
                    className="account-form"
                    onSubmit={createAccount}
                >

                    <h2>Add your first cloud account</h2>

                    <input
                        placeholder="Account name"
                        value={accountName}
                        onChange={e =>
                            setAccountName(e.target.value)
                        }
                        required
                    />

                    <button type="submit">
                        Add LocalStack Account
                    </button>

                </form>

            )}


            <section className="stats-grid">

                <div className="stat-card">

                    <span>Total Resources</span>

                    <h2>{resources.length}</h2>

                </div>


                <div className="stat-card">

                    <span>Active Resources</span>

                    <h2>{activeCount}</h2>

                </div>


                <div className="stat-card">

                    <span>Open Violations</span>

                    <h2>{violations.filter(
                        v => v.status === "open"
                    ).length}</h2>

                </div>


                <div className="stat-card">

                    <span>Critical Violations</span>

                    <h2>{criticalCount}</h2>

                </div>


                <div className="stat-card">

                    <span>Potential Monthly Savings</span>

                    <h2>
                        ₹{totalSavings.toLocaleString("en-IN")}
                    </h2>

                </div>

            </section>


            <section className="dashboard-grid">

                <div className="panel">

                    <h2>Resource Distribution</h2>

                    <ResponsiveContainer
                        width="100%"
                        height={300}
                    >

                        <BarChart data={resourceCounts}>

                            <CartesianGrid strokeDasharray="3 3" />

                            <XAxis dataKey="name" />

                            <YAxis allowDecimals={false} />

                            <Tooltip />

                            <Bar
                                dataKey="total"
                                fill="#3986F6"
                            />

                        </BarChart>

                    </ResponsiveContainer>

                </div>


                <div className="panel">

                    <h2>Recent Scan History</h2>

                    {scans.slice(0, 6).map(scan => (

                        <div
                            className="history-item"
                            key={scan.id}
                        >

                            <span>
                                {scan.status}
                            </span>

                            <span>
                                {scan.resources_scanned} resources
                            </span>

                            <small>
                                {new Date(
                                    scan.created_at
                                ).toLocaleString()}
                            </small>

                        </div>

                    ))}

                    {scans.length === 0 && (
                        <p>No scans performed yet.</p>
                    )}

                </div>

            </section>


            <section className="panel">

                <h2>Cloud Resource Inventory</h2>

                <div className="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>Resource ID</th>

                                <th>Type</th>

                                <th>Name</th>

                                <th>Region</th>

                                <th>State</th>

                            </tr>

                        </thead>

                        <tbody>

                            {resources.map(resource => (

                                <tr key={resource.id}>

                                    <td>{resource.resource_id}</td>

                                    <td>{resource.resource_type}</td>

                                    <td>{resource.resource_name}</td>

                                    <td>{resource.region}</td>

                                    <td>{resource.resource_state}</td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                    {resources.length === 0 && (
                        <p>No resources found. Run a scan first.</p>
                    )}

                </div>

            </section>


            <section className="panel">

                <h2>Security & Compliance Findings</h2>

                <div className="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>Policy ID</th>

                                <th>Resource</th>

                                <th>Severity</th>

                                <th>Description</th>

                                <th>Status</th>

                            </tr>

                        </thead>

                        <tbody>

                            {violations.map(item => (

                                <tr key={item.id}>

                                    <td>{item.policy_id}</td>

                                    <td>{item.resource_id}</td>

                                    <td>

                                        <span className={
                                            `severity ${item.severity}`
                                        }>
                                            {item.severity}
                                        </span>

                                    </td>

                                    <td>{item.description}</td>

                                    <td>{item.status}</td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                    {violations.length === 0 && (
                        <p>No violations detected in the latest completed scan.</p>
                    )}

                </div>

            </section>

        </div>

    );

}

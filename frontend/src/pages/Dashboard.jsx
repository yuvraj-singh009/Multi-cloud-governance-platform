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
import {
    startCloudScan,
    listAwsConnections,
    createAwsConnection,
    verifyAwsConnection,
    disconnectAwsConnection
} from "../services/api";

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
    const [connecting, setConnecting] = useState(false);
    const [verifying, setVerifying] = useState(false);
    const [disconnecting, setDisconnecting] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [accountName, setAccountName] = useState("");
    const [accountId, setAccountId] = useState("");
    const [region, setRegion] = useState("ap-south-1");
    const [roleArn, setRoleArn] = useState("");
    const [pendingConnection, setPendingConnection] = useState(null);

    const selectedConnection = accounts.find(account => account.id === selectedAccount);
    const selectedIsConnected = selectedConnection?.connection_status === "connected";

    function getApiError(err) {
        return err.response?.data?.detail || err.message || "Something went wrong.";
    }

    async function loadAccounts(preferredId = "") {
        try {
            const data = await listAwsConnections(session.access_token);
            setAccounts(data);
            const nextId = preferredId && data.some(item => item.id === preferredId)
                ? preferredId
                : data[0]?.id || "";
            setSelectedAccount(nextId);
        } catch (err) {
            console.error("AWS connection loading error:", err);
            setError(getApiError(err));
        } finally {
            setAccountsLoading(false);
        }
    }

    async function loadDashboard(accountIdToLoad) {
        if (!accountIdToLoad) {
            setScans([]);
            setResources([]);
            setViolations([]);
            setTotalSavings(0);
            setLoading(false);
            return;
        }

        setLoading(true);
        setError("");
        try {
            const { data: scanData, error: scanError } = await supabase
                .from("scan_jobs")
                .select("*")
                .eq("account_id", accountIdToLoad)
                .order("created_at", { ascending: false });
            if (scanError) throw scanError;

            const safeScans = scanData || [];
            setScans(safeScans);
            const latestScan = safeScans.find(scan => scan.status === "completed");

            if (!latestScan) {
                setResources([]);
                setViolations([]);
                setTotalSavings(0);
                return;
            }

            const { data: resourceData, error: resourceError } = await supabase
                .from("resource_snapshots")
                .select("*")
                .eq("scan_id", latestScan.id);
            if (resourceError) throw resourceError;
            setResources(resourceData || []);

            const { data: violationData, error: violationError } = await supabase
                .from("policy_violations")
                .select("*")
                .eq("scan_id", latestScan.id);
            if (violationError) throw violationError;
            setViolations(violationData || []);

            const { data: costData, error: costError } = await supabase
                .from("cost_estimates")
                .select("estimated_monthly_waste")
                .eq("scan_id", latestScan.id);
            if (costError) throw costError;

            setTotalSavings((costData || []).reduce(
                (total, item) => total + Number(item.estimated_monthly_waste || 0),
                0
            ));
        } catch (err) {
            setError(getApiError(err));
        } finally {
            setLoading(false);
        }
    }

    async function handleCreateConnection(event) {
        event.preventDefault();
        setError("");
        setNotice("");
        setConnecting(true);
        try {
            const created = await createAwsConnection({
                account_name: accountName.trim(),
                account_id: accountId.trim(),
                region: region.trim()
            }, session.access_token);

            // The backend returns the External ID only once. Keep it in component
            // state and show it immediately so the user can copy it for IAM setup.
            setPendingConnection(created);
            setRoleArn("");
            setAccountName("");
            setAccountId("");
            await loadAccounts(created.connection_id);
            setNotice("AWS connection created. Copy the External ID below before leaving this page.");
        } catch (err) {
            setError(getApiError(err));
        } finally {
            setConnecting(false);
        }
    }

    async function handleVerifyConnection(event) {
        event.preventDefault();
        if (!pendingConnection?.connection_id) return;
        setError("");
        setNotice("");
        setVerifying(true);
        try {
            const result = await verifyAwsConnection(
                pendingConnection.connection_id,
                roleArn.trim(),
                session.access_token
            );
            await loadAccounts(pendingConnection.connection_id);
            setPendingConnection(null);
            setRoleArn("");
            setNotice(`AWS account verified successfully: ${result.verified_account_id}`);
        } catch (err) {
            setError(getApiError(err));
        } finally {
            setVerifying(false);
        }
    }

    async function handleDisconnect(connectionId) {
        if (!window.confirm("Disconnect this AWS account? Existing scan history will remain in the database.")) {
            return;
        }
        setError("");
        setNotice("");
        setDisconnecting(true);
        try {
            await disconnectAwsConnection(connectionId, session.access_token);
            if (pendingConnection?.connection_id === connectionId) {
                setPendingConnection(null);
            }
            await loadAccounts("");
            setNotice("AWS account disconnected.");
        } catch (err) {
            setError(getApiError(err));
        } finally {
            setDisconnecting(false);
        }
    }

    async function handleScan() {
        if (!selectedAccount || !selectedIsConnected) return;
        setScanning(true);
        setError("");
        setNotice("");
        try {
            const result = await startCloudScan(selectedAccount, session.access_token);
            await loadDashboard(selectedAccount);
            setNotice(
                `Scan ${result.status}. Resources discovered: ${result.total_resources}. ` +
                (result.errors?.length ? `Collection errors: ${result.errors.length}.` : "No collection errors.")
            );
        } catch (err) {
            setError(getApiError(err));
        } finally {
            setScanning(false);
        }
    }

    useEffect(() => {
        if (session?.user?.id && session?.access_token) {
            loadAccounts();
        }
    }, [session?.user?.id, session?.access_token]);

    useEffect(() => {
        loadDashboard(selectedAccount);
    }, [selectedAccount]);

    const resourceCounts = Object.entries(resources.reduce((acc, item) => {
        acc[item.resource_type] = (acc[item.resource_type] || 0) + 1;
        return acc;
    }, {})).map(([name, total]) => ({ name, total }));

    const criticalCount = violations.filter(item => item.severity === "critical").length;
    const activeCount = resources.filter(item =>
        ["running", "available", "active", "associated"].includes(item.resource_state)
    ).length;

    if (accountsLoading || (loading && selectedAccount)) {
        return <div className="loading">Loading dashboard...</div>;
    }

    return (
        <div className="dashboard">
            <header className="topbar">
                <div>
                    <h1>Cloud Governance</h1>
                    <p>Cost optimization and security monitoring</p>
                </div>
                <button onClick={() => supabase.auth.signOut()} className="logout-button">
                    Logout
                </button>
            </header>

            {error && <p className="error-message" role="alert">{error}</p>}
            {notice && <p className="success-message" role="status">{notice}</p>}

            <section className="panel aws-connect-panel">
                <h2>Connect an AWS Account</h2>
                <p className="helper-text">
                    Connect your AWS account securely using an IAM role. Do not enter AWS access keys.
                </p>
                <form className="aws-connect-form" onSubmit={handleCreateConnection}>
                    <label>
                        Account display name
                        <input
                            value={accountName}
                            onChange={event => setAccountName(event.target.value)}
                            placeholder="Production AWS"
                            minLength={2}
                            maxLength={80}
                            required
                        />
                    </label>
                    <label>
                        12-digit AWS Account ID
                        <input
                            value={accountId}
                            onChange={event => setAccountId(event.target.value.replace(/\D/g, "").slice(0, 12))}
                            placeholder="123456789012"
                            inputMode="numeric"
                            pattern="[0-9]{12}"
                            maxLength={12}
                            required
                        />
                    </label>
                    <label>
                        AWS Region
                        <select value={region} onChange={event => setRegion(event.target.value)}>
                            <option value="ap-south-1">Asia Pacific (Mumbai) — ap-south-1</option>
                            <option value="ap-southeast-1">Asia Pacific (Singapore) — ap-southeast-1</option>
                            <option value="us-east-1">US East (N. Virginia) — us-east-1</option>
                            <option value="us-west-2">US West (Oregon) — us-west-2</option>
                            <option value="eu-west-1">Europe (Ireland) — eu-west-1</option>
                        </select>
                    </label>
                    <button type="submit" disabled={connecting}>
                        {connecting ? "Creating..." : "Create AWS Connection"}
                    </button>
                </form>

                {pendingConnection && (
                    <div className="external-id-box">
                        <h3>Step 2: Configure the IAM role in AWS</h3>
                        <p>
                            Copy this External ID now. It is shown only once by the backend.
                            Use it in the trust relationship for the IAM role you create in the customer AWS account.
                        </p>
                        <code>{pendingConnection.external_id}</code>
                        <button
                            type="button"
                            className="secondary-button"
                            onClick={() => navigator.clipboard.writeText(pendingConnection.external_id)}
                        >
                            Copy External ID
                        </button>
                        <form className="aws-verify-form" onSubmit={handleVerifyConnection}>
                            <label>
                                IAM Role ARN
                                <input
                                    value={roleArn}
                                    onChange={event => setRoleArn(event.target.value)}
                                    placeholder="arn:aws:iam::123456789012:role/CloudGovernanceAuditRole"
                                    required
                                />
                            </label>
                            <button type="submit" disabled={verifying}>
                                {verifying ? "Verifying with AWS..." : "Verify AWS Role"}
                            </button>
                        </form>
                    </div>
                )}
            </section>

            <section className="panel">
                <h2>Connected Cloud Accounts</h2>
                {accounts.length === 0 ? (
                    <p>No AWS accounts connected yet. Use the form above to add your first account.</p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Account</th>
                                    <th>AWS Account ID</th>
                                    <th>Region</th>
                                    <th>Status</th>
                                    <th>Verified</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {accounts.map(account => (
                                    <tr key={account.id}>
                                        <td>{account.account_name}</td>
                                        <td>{account.account_identifier}</td>
                                        <td>{account.region}</td>
                                        <td>
                                            <span className={`connection-status ${account.connection_status}`}>
                                                {account.connection_status}
                                            </span>
                                        </td>
                                        <td>{account.verified_at ? new Date(account.verified_at).toLocaleString() : "—"}</td>
                                        <td>
                                            <button
                                                type="button"
                                                className="danger-button"
                                                disabled={disconnecting}
                                                onClick={() => handleDisconnect(account.id)}
                                            >
                                                Disconnect
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
                {accounts.length > 0 && (
                    <div className="account-section">
                        <label htmlFor="selected-aws-account">Dashboard account</label>
                        <select
                            id="selected-aws-account"
                            value={selectedAccount}
                            onChange={event => setSelectedAccount(event.target.value)}
                        >
                            {accounts.map(account => (
                                <option key={account.id} value={account.id}>
                                    {account.account_name} ({account.connection_status})
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={handleScan}
                            disabled={!selectedAccount || !selectedIsConnected || scanning}
                        >
                            {scanning ? "Scanning..." : "Start Cloud Scan"}
                        </button>
                    </div>
                )}
                {selectedConnection && !selectedIsConnected && (
                    <p className="helper-text">
                        This account is pending verification. Complete the IAM role verification before scanning.
                        If you lost the one-time External ID, disconnect this pending connection and create it again.
                    </p>
                )}
            </section>

            <section className="stats-grid">
                <div className="stat-card"><span>Total Resources</span><h2>{resources.length}</h2></div>
                <div className="stat-card"><span>Active Resources</span><h2>{activeCount}</h2></div>
                <div className="stat-card"><span>Open Violations</span><h2>{violations.filter(v => v.status === "open").length}</h2></div>
                <div className="stat-card"><span>Critical Violations</span><h2>{criticalCount}</h2></div>
                <div className="stat-card">
                    <span>Potential Monthly Savings</span>
                    <h2>₹{totalSavings.toLocaleString("en-IN")}</h2>
                </div>
            </section>

            <section className="dashboard-grid">
                <div className="panel">
                    <h2>Resource Distribution</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={resourceCounts}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis allowDecimals={false} />
                            <Tooltip />
                            <Bar dataKey="total" fill="#3986F6" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                <div className="panel">
                    <h2>Recent Scan History</h2>
                    {scans.slice(0, 6).map(scan => (
                        <div className="history-item" key={scan.id}>
                            <span>{scan.status}</span>
                            <span>{scan.resources_scanned} resources</span>
                            <small>{new Date(scan.created_at).toLocaleString()}</small>
                        </div>
                    ))}
                    {scans.length === 0 && <p>No scans performed yet.</p>}
                </div>
            </section>

            <section className="panel">
                <h2>Cloud Resource Inventory</h2>
                <div className="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Resource ID</th><th>Type</th><th>Name</th><th>Region</th><th>State</th>
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
                    {resources.length === 0 && <p>No resources found. Verify an AWS account and run a scan first.</p>}
                </div>
            </section>

            <section className="panel">
                <h2>Security &amp; Compliance Findings</h2>
                <div className="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Policy ID</th><th>Resource</th><th>Severity</th><th>Description</th><th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {violations.map(item => (
                                <tr key={item.id}>
                                    <td>{item.policy_id}</td>
                                    <td>{item.resource_id}</td>
                                    <td><span className={`severity ${item.severity}`}>{item.severity}</span></td>
                                    <td>{item.description}</td>
                                    <td>{item.status}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {violations.length === 0 && <p>No violations detected in the latest completed scan.</p>}
                </div>
            </section>
        </div>
    );
}

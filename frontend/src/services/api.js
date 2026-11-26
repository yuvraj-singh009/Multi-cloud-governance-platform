import axios from "axios";

const API_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json"
    }
});

function authConfig(accessToken) {
    return {
        headers: {
            Authorization: `Bearer ${accessToken}`
        }
    };
}

export async function startCloudScan(accountId, accessToken) {
    const response = await api.post(
        `/api/v1/scans/${accountId}`,
        {},
        authConfig(accessToken)
    );
    return response.data;
}

export async function getResources(accountId, accessToken) {
    const response = await api.get(
        "/api/v1/resources/",
        {
            params: { account_id: accountId },
            ...authConfig(accessToken)
        }
    );
    return response.data.resources;
}

export async function listAwsConnections(accessToken) {
    const response = await api.get(
        "/api/v1/aws/connections",
        authConfig(accessToken)
    );
    return response.data.connections || [];
}

export async function createAwsConnection(payload, accessToken) {
    const response = await api.post(
        "/api/v1/aws/connections",
        payload,
        authConfig(accessToken)
    );
    return response.data;
}

export async function verifyAwsConnection(connectionId, roleArn, accessToken) {
    const response = await api.post(
        `/api/v1/aws/connections/${connectionId}/verify`,
        { role_arn: roleArn },
        authConfig(accessToken)
    );
    return response.data;
}

export async function disconnectAwsConnection(connectionId, accessToken) {
    const response = await api.delete(
        `/api/v1/aws/connections/${connectionId}`,
        authConfig(accessToken)
    );
    return response.data;
}

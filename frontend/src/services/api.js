import axios from "axios";

const API_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json"
    }
});


export async function startCloudScan(
    accountId,
    accessToken
) {

    const response = await api.post(
        `/api/v1/scans/${accountId}`,
        {},
        {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        }
    );

    return response.data;
}


export async function getResources(
    accountId,
    accessToken
) {

    const response = await api.get(
        "/api/v1/resources/",
        {
            params: {
                account_id: accountId
            },

            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        }
    );

    return response.data.resources;
}
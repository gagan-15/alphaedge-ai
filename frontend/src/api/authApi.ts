import axios from "axios";

const authApi = axios.create({
    baseURL: "http://127.0.0.1:8000/auth",
    timeout: 10000,
    withCredentials: true,
});

export interface LoginInput {
    email: string;
    password: string;
    device_name: string;
}

export interface RegistrationInput {
    full_name: string;
    email: string;
    password: string;
    country: string;
    accepts_terms: boolean;
    accepts_risk_disclosure: boolean;
    confirms_adult: boolean;
}

export async function loginAccount(input: LoginInput) {
    const response = await authApi.post("/login", input);
    return response.data;
}

export async function registerAccount(input: RegistrationInput) {
    const response = await authApi.post("/register", input);
    return response.data;
}

export async function verifyEmail(token: string) {
    const response = await authApi.post(
        "/email-verification/verify",
        { token },
    );
    return response.data;
}

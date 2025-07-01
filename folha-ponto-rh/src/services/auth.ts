import axios from 'axios';

const API = 'http://localhost:8000/auth';

export async function login(
  email: string,
  password: string
): Promise<{ access_token: string; token_type: string }> {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const response = await axios.post(`${API}/login`, params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });

  return response.data;
}

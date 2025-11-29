import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
    const { login } = useAuth();

    return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <h1>Hospital Secure Portal</h1>
            <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
                <button onClick={() => login('patient')} style={{ padding: '20px' }}>
                    Login as Patient
                </button>
                <button onClick={() => login('staff')} style={{ padding: '20px', background: '#ffdddd' }}>
                    Login as Staff
                </button>
            </div>
        </div>
    );
}
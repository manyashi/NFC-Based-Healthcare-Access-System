import { useState, useEffect } from 'react';
import api from '../api/axiosConfig';

export default function PatientDashboard() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // We need to create this endpoint in backend/app/routes/api.py or similar
        // For now, let's assume we add a route '/patient/my-history' 
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            // NOTE: You need to add this route to your backend!
            // It should be similar to the staff get_details but uses current_user.id
            const { data } = await api.get('/patient/my-history'); 
            setHistory(data);
        } catch (error) {
            console.error("Error", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading your records...</div>;

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">My Medical Records</h1>
            <div className="space-y-4">
                {history.map(entry => (
                    <div key={entry.id} className="border p-4 rounded shadow bg-white">
                        <div className="flex justify-between font-bold text-gray-700">
                            <span>{entry.hospital_name}</span>
                            <span>{new Date(entry.timestamp).toLocaleDateString()}</span>
                        </div>
                        <div className="text-sm text-gray-500 mb-2">
                            {entry.department} - {entry.type}
                        </div>
                        <p className="mt-2">{entry.details.notes}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
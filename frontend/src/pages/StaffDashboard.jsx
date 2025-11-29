import { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { useNavigate } from 'react-router-dom';

export default function StaffDashboard() {
    const [patients, setPatients] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchActivePatients();
    }, []);

    const fetchActivePatients = async () => {
        try {
            const { data } = await api.get('/staff/active-patients');
            setPatients(data);
        } catch (error) {
            console.error("Failed to fetch patients", error);
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Staff Dashboard - Active Access</h1>
            <p className="mb-4 text-gray-600">
                Below are patients who have authorized access via NFC within the last 24 hours.
            </p>

            {patients.length === 0 ? (
                <div className="bg-yellow-100 p-4 rounded">No active patients. Scan a patient's NFC tag to grant access.</div>
            ) : (
                <table className="min-w-full bg-white border">
                    <thead>
                        <tr className="bg-gray-100">
                            <th className="p-3 text-left">Patient Name</th>
                            <th className="p-3 text-left">Access Expires In</th>
                            <th className="p-3 text-left">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {patients.map(p => (
                            <tr key={p.id} className="border-t">
                                <td className="p-3 font-medium">{p.name}</td>
                                <td className="p-3 text-green-600 font-bold">
                                    {Math.floor(p.minutes_remaining / 60)}h {p.minutes_remaining % 60}m
                                </td>
                                <td className="p-3">
                                    <button 
                                        onClick={() => navigate(`/staff/patient/${p.id}`)}
                                        className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700"
                                    >
                                        Access Records
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}
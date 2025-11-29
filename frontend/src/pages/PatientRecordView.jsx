import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';

export default function PatientRecordView() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [record, setRecord] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    
    const [formData, setFormData] = useState({
        entry_type: 'Consultation',
        department: '',
        notes: '',
        prescription: ''
    });

    useEffect(() => {
        loadData();
    }, [id]);

    const loadData = async () => {
        try {
            const { data } = await api.get(`/staff/patients/${id}/details`);
            setRecord(data);
        } catch (error) {
            if (error.response?.status === 403) {
                alert("Access Expired!");
                navigate('/staff');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post(`/staff/patients/${id}/add-entry`, formData);
            alert("Record added securely.");
            setShowForm(false);
            setFormData({ entry_type: 'Consultation', department: '', notes: '', prescription: '' });
            loadData();
        } catch (error) {
            alert("Failed to save record.");
        }
    };

    if (loading) return <div>Loading Secure Records...</div>;

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold">{record.patient}</h1>
                    <span className="text-green-600 text-sm font-semibold">● Secure Access Active</span>
                </div>
                <button 
                    onClick={() => setShowForm(!showForm)}
                    className="bg-green-600 text-white px-6 py-2 rounded shadow hover:bg-green-700"
                >
                    + Add Medical Entry
                </button>
            </div>

            {showForm && (
                <div className="bg-gray-50 p-6 rounded border mb-8">
                    <h2 className="text-xl font-bold mb-4">New Medical Entry</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-bold">Type</label>
                                <select 
                                    className="w-full p-2 border rounded"
                                    value={formData.entry_type}
                                    onChange={e => setFormData({...formData, entry_type: e.target.value})}
                                >
                                    <option>Consultation</option>
                                    <option>Lab Test</option>
                                    <option>Admission</option>
                                    <option>Procedure</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-bold">Department</label>
                                <input 
                                    className="w-full p-2 border rounded"
                                    type="text" 
                                    placeholder="e.g. Cardiology"
                                    value={formData.department}
                                    onChange={e => setFormData({...formData, department: e.target.value})}
                                    required
                                />
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-bold">Clinical Notes</label>
                            <textarea 
                                className="w-full p-2 border rounded h-24"
                                placeholder="Diagnosis, observations..."
                                value={formData.notes}
                                onChange={e => setFormData({...formData, notes: e.target.value})}
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold">Prescription (Optional)</label>
                            <input 
                                className="w-full p-2 border rounded"
                                type="text"
                                placeholder="Medications..."
                                value={formData.prescription}
                                onChange={e => setFormData({...formData, prescription: e.target.value})}
                            />
                        </div>

                        <div className="flex justify-end gap-2">
                            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600">Cancel</button>
                            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Sign & Save</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="space-y-6">
                <h2 className="text-xl font-bold text-gray-700">Medical History Timeline</h2>
                {record.history.length === 0 ? <p className="text-gray-500">No medical history found.</p> : (
                    record.history.map((entry) => (
                        <div key={entry.id} className="border border-gray-200 bg-white shadow-sm rounded-lg overflow-hidden">
                            {/* Card Header: Hospital & Staff Info */}
                            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                                <div>
                                    <span className="font-bold text-gray-800 text-lg">{entry.hospital_name}</span>
                                    <span className="mx-2 text-gray-400">|</span>
                                    <span className="text-sm text-gray-600 font-medium">Dept: {entry.department}</span>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-bold text-gray-700">{entry.entry_type}</div>
                                    <div className="text-xs text-gray-500">{new Date(entry.timestamp).toLocaleString()}</div>
                                </div>
                            </div>

                            {/* Card Body: Medical Details */}
                            <div className="p-4">
                                <div className="mb-2">
                                    <p className="text-gray-800 whitespace-pre-line">{entry.details.notes}</p>
                                </div>
                                
                                {entry.details.prescription && (
                                    <div className="mt-3 bg-blue-50 p-2 rounded border border-blue-100 flex items-start">
                                        <span className="text-blue-600 font-bold mr-2">Rx:</span>
                                        <span className="text-blue-800">{entry.details.prescription}</span>
                                    </div>
                                )}
                                
                                <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400 flex justify-end">
                                    <span>Logged by: Staff ID #{entry.staff_name}</span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
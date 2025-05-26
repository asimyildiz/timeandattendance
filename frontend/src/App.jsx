import React, { useState } from 'react';
import axios from 'axios';
import ExceptionTable from './Exceptions';
import Message from './Message';

const apiBaseUrl = "http://127.0.0.1:8000"

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await axios.post(`${apiBaseUrl}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setData(response.data);
    } catch (err) {
      setError('Error uploading or processing file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Excel Exception Analyzer</h1>

      <input type="file" onChange={handleFileChange} className="mb-4" />
      <button
        onClick={handleSubmit}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Upload and Analyze
      </button>

      {loading && <div className="mt-4">Loading...</div>}
      {error && <div className="mt-4 text-red-600">{error}</div>}

      {data && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold mb-2">Results</h2>
          <p><strong>Employee           :</strong> {data.employee_name} ({data.employee_number})</p>
          <p><strong>Time Frame         :</strong> {data.first_date} - {data.last_date}</p>
          <p><strong># of Working Days  :</strong> {data.total_number_of_days}</p>
          <p><strong># of Late Entries  :</strong> {data.total_number_of_late_entries}</p>
          <p><strong># of Missing Hours :</strong> {data.total_missing_hours}</p>
          <p><strong># of Annual Leaves :</strong> {data.total_annual_leave}</p>
          <p><strong># of Sick Leaves   :</strong> {data.total_sick_leave}</p>


          <h3 className="text-lg font-semibold mt-4">Exceptions</h3>
          <ExceptionTable title={"MISSING DAYs"} exceptions={data.exceptions} kk={"MISSING_DAY"} canDisplayNote={true} />
          <ExceptionTable title={"LESS ENTRIEs"} exceptions={data.exceptions} kk={"LESS_ENTRY"} canDisplayNote={true} />
          <ExceptionTable title={"TOTAL OUTs"} exceptions={data.exceptions} kk={"TOTAL_OUT"} canDisplayNote={true} />
          <ExceptionTable title={"EARLY ENTRIEs"} exceptions={data.exceptions} kk={"EARLY_ENTRY"} />
          <ExceptionTable title={"LATE ENTRIEs"} exceptions={data.exceptions} kk={"LATE_ENTRY"} />

          <p><strong>Message:</strong> <Message message={data.message} /></p>
        </div>
      )}
    </div>
  );
}

import React from 'react';

const ExceptionTable = ({ title, exceptions, kk, canDisplayNote = false }) => {
    const filteredExceptions = exceptions?.filter(ex => ex[kk]);
    if (!filteredExceptions || filteredExceptions.length === 0) {
        return (
            <div className="overflow-x-auto border rounded shadow mb-6">
                <h3 className="text-lg font-semibold">{title}</h3>
                <p className="text-gray-500 italic">No exceptions to display.</p>
            </div>
        );
    }

    return (
        <div className="overflow-x-auto border rounded shadow mb-6">
            <h3 className="text-lg font-semibold mt-4">{title}</h3>
            <table className="min-w-full table-auto border-collapse">
                <thead className="bg-gray-100">
                    <tr>
                        <th className="border px-4 py-2 w-1/3">Date</th>
                        <th className="border px-4 py-2 w-1/3">Value</th>
                        {canDisplayNote && <th className="border px-4 py-2 w-1/3">Note</th>}
                    </tr>
                </thead>
                <tbody>
                    {exceptions
                        .filter(ex => ex[kk])
                        .map((ex, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                                <td className="border px-4 py-2 w-1/3">{ex.DATE}</td>
                                <td className="border px-4 py-2 w-1/3">{ex[kk] || '-'}</td>
                                {canDisplayNote && <td className="border px-4 py-2 w-1/3">{ex.NOTE || '-'}</td>}
                            </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ExceptionTable;

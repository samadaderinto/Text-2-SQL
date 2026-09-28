import { useState, useEffect } from 'react';
import { Header } from "../layouts/Header";
import { useLocation } from 'react-router-dom';
import Sidebar from '../layouts/Sidebar';

type QueryPlan = {
  intent?: string;
  resource?: string;
  search?: string;
  filters?: Record<string, unknown>;
  sort?: string;
  limit?: number;
};

type QueryResponse = {
  status?: string;
  message?: string;
  transcript?: string;
  plan?: QueryPlan;
  sql_preview?: string;
  total_count?: number;
  results?: any[];
};

const Query = () => {
  const location = useLocation();
  const [dataArray, setDataArray] = useState<any[]>([]);
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);

  useEffect(() => {
    const response = location.state?.queryResponse as QueryResponse | undefined;
    const data = response?.results ?? location.state?.data;

    setQueryResponse(response ?? null);

    if (typeof data === 'string') {
      try {
        const parsedData = JSON.parse(data);
        if (Array.isArray(parsedData)) {
          setDataArray(parsedData);
        } else {
          console.error('Parsed data is not an array');
        }
      } catch (error) {
        console.error('Error parsing JSON string:', error);
      }
    } else if (Array.isArray(data)) {
      setDataArray(data);
    } else {
      setDataArray([]);
    }
  }, [location.state]);

  const convertToCSV = (array: any[]) => {
    if (array.length === 0) return '';

    const keys = Object.keys(array[0]); 
    const csvRows = [keys.join(',')];

    array.forEach(item => {
      const values = keys.map(key => `"${item[key]}"`);
      csvRows.push(values.join(','));
    });

    return csvRows.join('\n');
  };

  const downloadCSV = () => {
    const csv = convertToCSV(dataArray);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', 'data.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <>
      <Header />
      <Sidebar />
      <div className="Query_Container">
        <section className="Query_Header">
          <h1>{location.state?.header ?? 'Query Results'}</h1>
          <button
            className="Query_Download_Btn"
            onClick={downloadCSV}
            disabled={dataArray.length === 0}
          >
            Download
          </button>
        </section>

        <section className="Query_Item_Container">
          {queryResponse && (
            <div className="Query_Summary">
              {queryResponse.transcript && (
                <p>
                  <strong>Transcript</strong>
                  <span>{queryResponse.transcript}</span>
                </p>
              )}
              {queryResponse.message && (
                <p>
                  <strong>Status</strong>
                  <span>{queryResponse.message}</span>
                </p>
              )}
              {queryResponse.plan && (
                <div className="Query_Plan">
                  <strong>Plan</strong>
                  <div>
                    <span>{queryResponse.plan.intent ?? 'search'}</span>
                    <span>{queryResponse.plan.resource ?? 'records'}</span>
                    <span>limit {queryResponse.plan.limit ?? dataArray.length}</span>
                    {queryResponse.plan.sort && <span>sort {queryResponse.plan.sort}</span>}
                  </div>
                </div>
              )}
              {queryResponse.sql_preview && (
                <details>
                  <summary>SQL preview</summary>
                  <pre>{queryResponse.sql_preview}</pre>
                </details>
              )}
            </div>
          )}

          {dataArray.length > 0 ? (
            <>
              <div className="Query_Headers">
                {Object.keys(dataArray[0]).map((header, idx) => (
                  <strong key={idx} >
                    {header.replace(/_/g, ' ')}
                  </strong>
                ))}
              </div>
              <ul>
                {dataArray.map((item, index) => (
                  <li key={index}>
                    {Object.entries(item).map(([_, value], idx) => (
                      <div key={idx}>
                        {value?.toString() || 'N/A'}
                      </div>
                    ))}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p>No data available</p>
          )}
        </section>
      </div>
    </>
  );
};

export default Query;

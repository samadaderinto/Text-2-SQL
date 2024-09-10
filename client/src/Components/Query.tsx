import { useState, useEffect } from 'react';
import { Header } from "../layouts/Header";
import { useLocation } from 'react-router-dom';
import SideBar from '../layouts/SideBar';

const Query = () => {
  const location = useLocation();
  const [dataArray, setDataArray] = useState<any[]>([]);

  useEffect(() => {
    const data = location.state?.data;

    if (typeof data === 'string') {
      try {
        const parsedData = JSON.parse(data);
        if (Array.isArray(parsedData)) {
          setDataArray(parsedData); // Set the parsed data as an array
        } else {
          console.error('Parsed data is not an array');
        }
      } catch (error) {
        console.error('Error parsing JSON string:', error);
      }
    } else if (Array.isArray(data)) {
      setDataArray(data); 
    } else {
      console.error('No data available or data is not a string or array');
    }
  }, [location.state]);

  const convertToCSV = (array: any[]) => {
    if (array.length === 0) return '';

    const keys = Object.keys(array[0]); // Get the keys from the first object (headers)
    const csvRows = [keys.join(',')]; // Create the header row

    // Loop through the array and push the values for each row
    array.forEach(item => {
      const values = keys.map(key => `"${item[key]}"`); // Escape values and add quotes
      csvRows.push(values.join(','));
    });

    return csvRows.join('\n'); // Join rows by new lines
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
    document.body.removeChild(a); // Clean up the DOM after triggering the download
  };

  return (
    <>
      <Header />
      <SideBar />
      <div className="Query_Container">
        <section className="Query_Header">
          <h1>Query Request Items</h1>
          <button className="Query_Download_Btn" onClick={downloadCSV}>Download</button>
        </section>

        <section className="Query_Item_Container">
          {dataArray.length > 0 ? (
            <>
              <div className="Query_Headers">
                {Object.keys(dataArray[0]).map((header, idx) => (
                  <strong key={idx} className=''>
                    {header.replace(/_/g, ' ')}
                  </strong>
                ))}
              </div>
              <ul>
                {dataArray.map((item, index) => (
                  <li key={index}>
                    {Object.entries(item).map(([key, value], idx) => (
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

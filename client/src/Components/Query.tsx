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
      setDataArray(data); // If it's already an array, set it directly
    } else {
      console.error('No data available or data is not a string or array');
    }
  }, [location.state]);

  return (
    <>
      <Header />
      <SideBar />
      <div className="Query_Container">
        <section className="Query_Header">
          <h1>Query Request Items</h1>
          <button className="Query_Download_Btn">Download</button>
        </section>
        <section className="Query_Item_Container">
          {dataArray.length > 0 ? (
            <ul>
              {dataArray.map((item, index) => (
                <li key={index}>
                  {Object.entries(item).map(([key, value], idx) => (
                    <div key={idx}>
                      <strong>{key.replace(/_/g, ' ')}:</strong> {value?.toString() || 'N/A'}
                    </div>
                  ))}
                </li>
              ))}
            </ul>
          ) : (
            <p>No data available</p>
          )}
        </section>
      </div>
    </>
  );
};

export default Query;

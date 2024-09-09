import { useState, useEffect } from 'react';
import { Header } from "../layouts/Header";
import ReactPaginate from "react-paginate";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import SideBar from "../layouts/SideBar";
import { FiSearch } from 'react-icons/fi';
import {  MdOutlineDownload } from "react-icons/md";

import { ClipLoader } from 'react-spinners'; // Importing ClipLoader from react-spinners

const Query = () => {
  const items: any[] = []; // Simulate empty items
  const itemsPerPage = 5;

  const [currentPage, setCurrentPage] = useState(0);
  const [loading, setLoading] = useState<boolean>(true); // Loading state

  const totalPages = Math.ceil(items.length / itemsPerPage);
  const offset = currentPage * itemsPerPage;
  const currentItems = items.slice(offset, offset + itemsPerPage);

  useEffect(() => {
    setLoading(true); // Start loading
    setTimeout(() => {
      // Simulate fetching data
      // items would be updated here with the fetched data
      setLoading(false); // Stop loading after data is "fetched"
    }, 2000); // Simulating delay
  }, []);

  const handlePageClick = ({ selected }: { selected: number }) => {
    setCurrentPage(selected);
  };

  return (
    <>
      <Header />
      <SideBar />
      <div className="Query_Container">
        <section className="Query_Header">
          <h1>Items</h1>
          <button className="Query_Download_Btn">Download <MdOutlineDownload style={{fontSize:'24px'}}/></button>
        </section>

        <section className='Query_Body'>
          <div className='Input_Holder'>
            <FiSearch style={{cursor: 'pointer'}}/>
            <input type="text" placeholder='Search Name' name="" id="" />
          </div>
          <div className="Query_Form_Header">
            <span className='Query_Name'>
              <input type="checkbox" name="" id="" />
              <p>Product Name</p>
            </span>
            <ul>
              <li>Category</li>
              <li>Status</li>
              <li>Price</li>
              <li>Sold</li>
              <li>Sales</li>
              <li>Action</li>
            </ul>
          </div>
        {loading ? (
          <div className="spinner-container">
            <ClipLoader color={"#123abc"} loading={loading} size={50} />
          </div>
        ) : (
          <>
           
            <section className="Query_Item_container">
              {currentItems.length > 0 ? (
                currentItems.map((item: any, index: number) => (
                  <div key={index}>Item {index + 1}</div> 
                ))
              ) : (
                <p style={{marginLeft:'-45%'}}>No items available</p>
              )}
            </section>

            {totalPages > 1 && (
              <ReactPaginate
                previousLabel={<FaAngleLeft className="order_arrow" />}
                nextLabel={<FaAngleRight className="order_arrow" />}
                breakLabel={'...'}
                pageCount={totalPages}
                marginPagesDisplayed={2}
                pageRangeDisplayed={5}
                onPageChange={handlePageClick}
                containerClassName={'Product_pagination'}
                activeClassName={'Product_page_active'}
                previousClassName={'pagination_arrow'}
                nextClassName={'pagination_arrow'}
                disabledClassName={'pagination_disabled'}
              />
            )}
          </>
          
        )}
        </section>
      </div>
    </>
  );
};

export default Query;

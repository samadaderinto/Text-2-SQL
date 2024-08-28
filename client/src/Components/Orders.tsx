import axios from "axios";
import { useEffect, useState } from "react";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import { HiMiniMagnifyingGlass } from "react-icons/hi2";
import { MdOutlineDelete, MdOutlineDownload } from "react-icons/md";
import ReactPaginate from 'react-paginate';
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/SideBar";
import api from "../utils/api";


export const Orders = () => {
  const itemsPerPage = 15;
  const [input, setInput] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [data, setData] = useState<any[]>([]);


  useEffect(() => {
    fetchData();
  }, [currentPage]);

  const fetchData = async () => {
    const offset = currentPage * itemsPerPage;

    try {
      const response = await api.get(
        `/orders/search/?offset=${1}&limit=${itemsPerPage}`,
      );
      setData(response.data);
      console.log(response)
    
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handlePageClick = (event: { selected: number }) => {
    setCurrentPage(event.selected);
  };

  return (
    <>
      <Header />
      <div className="Order_Container">
        <Sidebar />
        <section className="Order_Header">
          <h1>Order</h1>
          <span>
            <MdOutlineDownload className="Order_Download_Icon" />
            Download List
          </span>
        </section>
        <section className="Order_List_Container">
          <ul>
            <li>All Orders</li>
            <li>Pending</li>
            <li>Paid</li>
            <li>Cancelled</li>
          </ul>
          <div className="Order_Search_Box">
            <HiMiniMagnifyingGlass />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Search Orders"
            />
          </div>

          <div className="Order_List_Header">
            <article>
              <input type="checkbox" />
              <p>Order ID</p>
              <p>Customer Name</p>
            </article>
            <article className="Order_Attributes">
              <p>Status</p>
              <p>Date & Time</p>
              <p>Price</p>
              <p>Action</p>
            </article>
          </div>

          <div className="Order_List_Item">
            {data.map((orderItem: any, index: number) => (
              <article key={index}>
                <input type="checkbox" />
                <p style={{ color: 'black' }}>{orderItem.id}</p>
                <span>
                  <img src={orderItem.img} alt="" />
                </span>
                <p style={{ color: 'black' }}>Wahab Adetunji</p>
                <p className="Order_Status">{orderItem.status}</p>
                <p>{orderItem.created.substring(0, 10)}</p>
                <p>{orderItem.subTotal}</p>
                <p className="Order_Icon_action">
                  <MdOutlineDownload />
                  <MdOutlineDelete />
                </p>
              </article>
            ))}

            <ReactPaginate 
              previousLabel={<FaAngleLeft className="order_arrow"/>}
              nextLabel={<FaAngleRight className="order_arrow"/>}
              breakLabel={'...'}
              pageCount={Math.ceil(data.length / itemsPerPage)}
              marginPagesDisplayed={2}
              pageRangeDisplayed={5}
              onPageChange={handlePageClick}
              containerClassName={'Order_pagination'}
              activeClassName={'Order_page_active'}
            />
          </div>
        </section>
      </div>
    </>
  );
};

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
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    fetchData();
  }, [currentPage, input]);

  const fetchData = async () => {

    const offset = currentPage * itemsPerPage;
    try {
      const response = await api.get(`/orders/search/?offset=${offset}&limit=${itemsPerPage}&search=${input}`);
      setData(response.data);
      console.log(response.data)
      setTotalItems(response.data.count);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handlePageClick = (event: { selected: number }) => {
    setCurrentPage(event.selected);
  };



  const handleDownload = async (order_id = "") => {

    try {
      const end_point = order_id ? `/orders/download/${order_id}/` : "/orders/download/"
      const response = await api.get(end_point, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'orders.csv');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  const handleDelete = async (order_id: any) => {
    try {
      const response = await api.delete(`/orders/delete/${order_id}/`)

      if (response.status === 205) {
        setData(data.filter((item) => item.id !== order_id));
        setTotalItems(totalItems - 1);
      }


    } catch (error) {
      console.error("Error delete:", error);
    }

  }

  return (
    <>
      <Header />
      <div className="Order_Container">
        <Sidebar />
        <section className="Order_Header">
          <h1>Orders</h1>
          <span onClick={() => handleDownload}>
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
              <p className='Header_customer_Name'>Customer Name</p>
            </article>
            <div className="Order_Attributes">
              <p>Status</p>
              <p>Date & Time</p>
              <p>Price</p>
              <p>Action</p>
            </div>
          </div>

          <div className="Order_List_Item">
            {data.map((orderItem: any, index: number) => (
              <article key={index}>
                <input type="checkbox" />
                <p style={{ color: 'black' }}>{orderItem.id}</p>
                <p style={{ color: 'black' }}>{orderItem.name}</p>
                <p className="Order_Status">{orderItem.status}</p>
                <p>{orderItem.created.substring(0, 10)}</p>
                <p>{orderItem.subtotal}</p>
                <p className="Order_Icon_action">
                  <MdOutlineDownload onClick={() => handleDownload(orderItem.id)} />
                  <MdOutlineDelete onClick={() => handleDelete(orderItem.id)} />
                </p>
              </article>
            ))}

            <ReactPaginate
              previousLabel={<FaAngleLeft className="order_arrow" />}
              nextLabel={<FaAngleRight className="order_arrow" />}
              breakLabel={'...'}
              pageCount={Math.ceil(totalItems / itemsPerPage)}
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

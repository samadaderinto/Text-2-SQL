import axios from "axios";
import ReactPaginate from "react-paginate";
import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import { FaAngleRight, FaAngleLeft } from "react-icons/fa";
import { FiSearch } from "react-icons/fi";
import { useState, useEffect } from "react";
import { Header } from "../layouts/Header";
import Sidebar from '../layouts/SideBar';
import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { CustomerProps } from "../types/customers";



export const Customers = () => {
  const itemsPerPage = 15;
  const [data, setData] = useState<CustomerProps[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const nav = useNavigate();

  const fetchData = async () => {
    const offset = currentPage * itemsPerPage;
    try {
      const response = await api.get(`/customers/search/?offset=${offset}&limit=${itemsPerPage}`, {

      });
      console.log("Fetched data:", response.data); // Debugging line
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentPage]);

  const handlePageClick = (event: { selected: number }) => {
    setCurrentPage(event.selected);
  };

  return (
    <>
      <Header />
      <Sidebar />

      <div className="Customer_Container">
        <article>
          <h1>Customers</h1>
          <span onClick={() => nav('/customers/add')}><IoIosAddCircleOutline className="Circle_Icon" /> Add New Customers</span>
        </article>

        <section className="Customer_List_Container">
          <article>
            <div>
              <FiSearch />
              <input className="Search_Icon_Input" type="text" placeholder="Search Name" />
            </div>
            <MdOutlineCalendarToday className="Customer_Calendar" />
          </article>

          <article className="Customer_List_Header">
            <div>
              <input type="checkbox" />
              <p>ID</p>
              <p>Customer Name</p>
            </div>
            <p>Email</p>
            <div>
              <p className="Date_Joined">Date Joined</p>
              <p>Orders</p>
              <p>Spending</p>
            </div>
            <p>Action</p>
          </article>
          <section className="Customer_List">
            {
              data.map((item) => (
                <article key={item.id}>
                  <span>
                    <input type="checkbox" />
                    <p className="Id_customer">{item.id}</p>
                    <div>
                      <img src="" alt="" />
                    </div>
                    <p>{item.name}</p>
                  </span>
                  <p>{item.email}</p>
                  <span>
                    <p className="Date_Joined">{item.dateJoined}</p>
                    <p>{item.orders} Orders</p>
                    <p>${item.spending}</p>
                  </span>
                  <p className="Customer_Action_Icon">
                    <MdOutlineEdit />
                    <MdOutlineDelete />
                  </p>
                </article>
              ))
            }

            <ReactPaginate
              previousLabel={<FaAngleLeft className="customer_arrow"/>}
              nextLabel={<FaAngleRight className="customer_arrow"/>}
              breakLabel={'...'}
              pageCount={Math.ceil(data.length / itemsPerPage)}
              marginPagesDisplayed={2}
              pageRangeDisplayed={5}
              onPageChange={handlePageClick}
              containerClassName={'Customer_pagination'}
              activeClassName={'Order_page_active'}
            />
          </section>
        </section>
      </div>
    </>
  );
};

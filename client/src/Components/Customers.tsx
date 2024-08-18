import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import { FiSearch } from "react-icons/fi";
import { useState, useEffect } from "react";
// import { Newcustomer } from "./Newcustomer";
import { Header } from "../layouts/Header"
import Sidebar from '../layouts/SideBar'
import { API_BASE_URL } from "../utils/api";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import ReactPaginate from "react-paginate";
// import { Header } from "../layouts/Header";




export const Customers = () => {
  const itemsPerPage = 15;
  // const [newcustomer, setNewcustomer] = useState(false)
  const [datas, setData] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const access = localStorage.getItem('access')
  const accessToken = JSON.stringify({ access });
  const Nav = useNavigate()

  
  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/customers/search/?offset=${offset}&limit=${itemsPerPage}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        }
      })
      const datum: string[] = response.data;

      setData(datum)
    }
    catch (error) {
      console.error("error fetching data", error)
    }
  }

  useEffect(() => {
    fetchData()

  }, [])
  

  const offset = currentPage * itemsPerPage;

  interface PageClickEvent {
    selected: number;
  }

  const handlePageClick = (event:PageClickEvent) => {
    const selectedPage = event.selected;
    setCurrentPage(selectedPage);
  };

  
  return (
    <>
    <Header/>
    <Sidebar/>

        <div className="Customer_Container">
      <article>
        <h1>Customers</h1>
        <span onClick={()=> Nav('/customers/add')}><IoIosAddCircleOutline className="Circle_Icon"/> Add New Customers</span>
      </article>

      <section className="Customer_List_Container">
       <article>
       <div>
          <FiSearch/>
          <input className="Search_Icon_Input" type="text" placeholder="Search Name" />
        </div>
        <MdOutlineCalendarToday className="Customer_Calendar"/>
       </article>

       <article className="Customer_List_Header">
        <div>
          <input type="checkbox" name="" id="" />
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
        datas.map((item, index)=>(
          <article key={index}>
          <span>
            <input type="checkbox" name="" id="" />
            <p className="Id_customer">ID12344</p>
            <div>
              <img src="" alt="" />
            </div>
            <p>Iyanda Wahab</p>
          </span>
          <p>ronin@gmai.com</p>
          <span>
            <p className="Date_Joined">July 20 2024</p>
            <p>50 Orders</p>
            <p>$23,000</p>
          </span>
          <p className="Customer_Action_Icon">
            <MdOutlineEdit/>
            <MdOutlineDelete/>
          </p>
          </article>
        ))
       }

<ReactPaginate
        previousLabel={'previous'}
        nextLabel={'next'}
        breakLabel={'...'}
        pageCount={Math.ceil(datas.length / itemsPerPage)}
        marginPagesDisplayed={2}
        pageRangeDisplayed={5}
        onPageChange={handlePageClick}
        containerClassName={'Order_pagination'}
        activeClassName={'Order_page_active'}
      />
       </section>
      </section>
    </div>
    
    </>
  )
} 
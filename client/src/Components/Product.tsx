import { ReactEventHandler, useState } from 'react';
import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import { FiSearch } from "react-icons/fi";
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/SideBar";
import { useNavigate } from "react-router-dom";
import ReactPaginate from 'react-paginate';
import { API_BASE_URL } from "../utils/api";
import axios from 'axios'



export const Product = () => {
  const [currentPage, setCurrentPage] = useState(0)
  const itemsPerPage = 15;
  const offset = currentPage * itemsPerPage;
  const [input, setInput] = useState('')
  const strInput = JSON.stringify({input})

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/products/search/?offset=${offset}&limit=${itemsPerPage}`, {strInput}, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        }
      })
      const data = response.data;

      return data;
    }
    catch (error) {
      console.error("error fetching data", error)
    }
  }

  fetchData()

  // const currentItems = data.slice(offset, offset + itemsPerPage);
 

  const handlePageClick = (event: ReactEventHandler) => {
    const selectedPage = event.selected;
    setCurrentPage(selectedPage);
  };

  const access = localStorage.getItem('access')
  const accessToken = JSON.stringify({ access });
  const Nav = useNavigate()
  return (
      <div className="Product_Container">
        <Header/>
        <Sidebar/>
      <section className="Add_Product">
        <h1>All Products</h1>
        <span onClick={()=> Nav('/product/add') }> <IoIosAddCircleOutline className="Product_Icon"/>Add new Product</span>
      </section>
      <section className="Product_Table_Section">
        <div>
          <span>
            <FiSearch className="Search_Icon"/>
          <input type="text" value={input} onChange={(e)=>{
            setInput(e.target.value)
            

          }} placeholder="Search Name" />
          </span>
          <MdOutlineCalendarToday/>
        </div>
        <div className="Product_Table_list_header">
          <span>
            <input type="checkbox" />
            <p>Product Name</p>
          </span>
          <ul>
            <li>Category</li>
            <li>Status</li>
            <li>Price</li>
            <li>Sold</li>
            <li>Sales</li>
          </ul>
          <p>Action</p>
        </div>
        <div className="Product_Table_List_content">
        {
          data.map((key, index)=>(
            <nav key={index}>
            <span>
               <input type="checkbox" />
               <article className="Product_Img_Container">
               <img src="" alt="" />
               </article>
               <p>Gold Stainless Spoons & Forks</p> 
             </span>
             <span className="Product_Details">
               <p className="Product_Category">Furniture</p>
               <p className="Product_Available">available</p>
               <p>$500</p>
               <p>335</p>
               <p>$15643.00</p>
             </span>
             <p className="Product_Icons">
               <MdOutlineEdit/>
               <MdOutlineDelete/>
             </p>
            </nav>
          ))
        }

<ReactPaginate
        previousLabel={'previous'}
        nextLabel={'next'}
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


   
      
    )
}
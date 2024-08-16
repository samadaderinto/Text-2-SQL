import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import { FiSearch } from "react-icons/fi";
// import { useState } from "react";
// import { Newproduct } from "./Newproduct";
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/SideBar";
import { useNavigate } from "react-router-dom";



export const Product = () => {
  // const [newproduct, setNewproduct] = useState(false)
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
          <input type="text" placeholder="Search Name" />
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
        </div>
      </section>
    </div>


   
      
    )
}
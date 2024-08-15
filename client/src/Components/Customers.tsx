import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import { FiSearch } from "react-icons/fi";
import { useState } from "react";
import { Newcustomer } from "./Newcustomer";



export const Customers = () => {
  const [newcustomer, setNewcustomer] = useState(false)
  return (
    <>
    {
      !newcustomer ?(
        <div className="Customer_Container">
      <article>
        <h1>Customers</h1>
        <span onClick={()=> !newcustomer? setNewcustomer(true): null}><IoIosAddCircleOutline className="Circle_Icon"/> Add New Customers</span>
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
        <article>
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
       </section>
      </section>
    </div>
      ): (<Newcustomer/>)

    }
    
    </>
  )
} 
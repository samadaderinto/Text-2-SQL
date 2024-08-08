import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import { FiSearch } from "react-icons/fi";



export const Customers = () => {
  return (
    <div className="Customer_Container">
      <article>
        <h1>Customers</h1>
        <span><IoIosAddCircleOutline className="Circle_Icon"/> Add New Customers</span>
      </article>

      <section className="Customer_List_Container">
        <div>
          <FiSearch/>
          <input type="text" placeholder="Search Name" />
        </div>
        <MdOutlineCalendarToday className="Customer_Calendar"/>
      </section>
    </div>
  )
} 
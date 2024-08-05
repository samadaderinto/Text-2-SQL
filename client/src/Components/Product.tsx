import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday } from "react-icons/md";
import { FiSearch } from "react-icons/fi";

export const Product = () => {
  return (
    <div className="Product_Container">
      <section className="Add_Product">
        <h1>All Products</h1>
        <span> <IoIosAddCircleOutline className="Product_Icon"/>Add new Product</span>
      </section>
      <section className="Product_Table_Section">
        <div>
          <span>
            <FiSearch className="Search_Icon"/>
          <input type="text" placeholder="Search Name" />
          </span>
          <MdOutlineCalendarToday/>
        </div>
        <div></div>
      </section>
    </div>
  )
}
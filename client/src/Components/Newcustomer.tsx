// import React from 'react'
import { useState } from "react";
import { LuImagePlus } from "react-icons/lu";

export const Newcustomer = () => {
  const [img, setImg] = useState<string | null>(null)

  const Upload = (e :React.ChangeEvent<HTMLInputElement>)=> {
    if(e.target.files && e.target.files.length > 0) {
      // const File = e.target.files[0]
      const url = URL.createObjectURL(e.target.files[0])
      setImg(url)
      console.log(img)

    }

    // useEffect(()=> {
    //   if(img) {
    //     console.log(img)
    //   }
    // })[img]
   
  
  }
  return (
    <div className="Newproduct_Container">
      <h1>Create New Customer</h1>
      <section className="Product_Form_Container">
        <div className="GenProduct_Container">
          <h3> Customer Information</h3>
          <form action="">
            <label htmlFor="First_Name">First Name </label>
            <input type="text" placeholder="input customer first name" id="First_Name" />
            <label htmlFor="Last_Name">Last Name</label>
           <input type="text" id="Last_Name" placeholder="input customer last name" />
           <label htmlFor="customer_Email">Last Name</label>
           <input type="text" id="customer_Email" placeholder="input customer Email" />
           <label htmlFor="customer_phone">Last Name</label>
           <input type="text" id="customer_phone" placeholder="input customer phone number" />
              <div>
                <span className="Cancel_Btn">Cancel</span>
                <span className="Add_Btn">Add Product</span>
              </div>
          </form>
        </div>
        <div className="Product_Media_Container">
          <h3>Customer Image</h3>
          <section>
         
            {
              img === null ? 
              <>
               <label htmlFor="fileInput">
          <input type="file" onChange={Upload} style={{display: "none"}}  id="fileInput" />
              <LuImagePlus/>
              <p>click or drag image</p>
              </label>
              </>
              : <img src={img} alt="" />
            }
            
          </section>
         <span>
           <label htmlFor="Category">Date Added</label>
            <select name="Select Date Added" id="Category">
              <option value="" disabled>Date added</option>
              <option value=""></option>
              <option value=""></option>
              <option value=""></option>
              <option value=""></option>
            </select>
           <label htmlFor="quantity">Product Quantity</label>
              <input type="text" placeholder="Input Product Quantity"/>
          </span>
        </div>
        
      </section>
    </div>
  )
}

// import React from 'react'
import { useState } from "react";
import { LuImagePlus } from "react-icons/lu";

export const Newproduct = () => {
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
      <h1>Create New Product</h1>
      <section className="Product_Form_Container">
        <div className="GenProduct_Container">
          <h3>General Product Information</h3>
          <form action="">
            <label htmlFor="Product_Name">Product Name </label>
            <input type="text" placeholder="input product name" id="Product_Name" />
            <label htmlFor="Product_Description">Product Description</label>
            <textarea name="Product_Description" placeholder="Describe the product" id="Product_Description"></textarea>
            <span>
             <article className="Select_Article">
             <label htmlFor="currency">currency</label>
              <select name="currency" id="currency">
              <option value="$">$</option>
              <option value="£">£</option>
              <option value="€">€</option>
              </select> 
             </article>
              <article className="Price_Article">
                <label htmlFor="product_price">product price</label>
                <input type="text" id="product_price" placeholder="input price" />
              </article>
              
              </span>
              <div>
                <span className="Cancel_Btn">Cancel</span>
                <span className="Add_Btn">Add Product</span>
              </div>
          </form>
        </div>
        <div className="Product_Media_Container">
          <h3>Product Media</h3>
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
           <label htmlFor="Category">Product Category</label>
            <select name="Select Product Category" id="Category">
              <option value="" disabled>Select product category</option>
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

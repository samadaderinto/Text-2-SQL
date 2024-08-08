import { useState } from "react"

export const Settings = () => {
  const [active, setActive] = useState('General')
  return (
    <div className="Settings_Container">
      <h1>Settings</h1>
      <ul>
        <li className={active === 'General'? 'Active': ''} onClick={()=> {active !== 'General'? setActive('General'): null}}>General</li>
        <li  className={active === 'Account'? 'Active': ''} onClick={()=> {active !== 'Account'? setActive('Account'): null}}>Account</li>
        <li className={active === 'Notifications'? 'Active': ''} onClick={()=> {active !== 'Notifications'? setActive('Notifications'): null}}>Notifications</li>
      </ul>

      <form action="">
       {
        active === 'General'? 
        <>
         <h3>General Information</h3>
        <label htmlFor="Store_Name">Store Name</label>
        <input type="text" placeholder="Input store Name" name="" id="Store_Name" />
        <label htmlFor="Store_Email">Store Email</label>
        <input type="email" placeholder="Input store email" />
        <label htmlFor="currency">Currency</label>
        <select name="" id="currency">
          <option value="$">$</option>
          <option value="£">£</option>
          <option value="€">€</option>
        </select>
        </> : active === 'Account'?
        <>
                 <h3>Account Information</h3>
        <label htmlFor="Admin_Name">Admin Name</label>
        <input type="text" placeholder="Input Admin Name" name="" id="Admin_Name" />
        <label htmlFor="Admin_Email"> Email Address</label>
        <input type="email" placeholder="Input email" />
        <label htmlFor="password">Password
        <p>change password</p>
        </label>
       <input type="password" placeholder="password" name="" id="password" />
      
        </> : 
        <>
        <h3>Notifications</h3>
        <section className="Notify_Section">
        <input type="checkbox" name="" id="" />
        <p>Enable Email Notifications</p>
        <input type="checkbox" name="" id="" />
        <p>Enable SMS Notifications</p>
        </section>
        </>
       }
        <div>
          <span className="White_Btn">Cancel</span>
          <span className="Blue_Btn">Save Changes</span>
        </div>
      </form>
    </div>
  )
}


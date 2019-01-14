<?php

namespace ICT\Core\Api;

/* * ***************************************************************
 * Copyright © 2016 ICT Innovations Pakistan All Rights Reserved   *
 * Developed By: Nasir Iqbal                                       *
 * Website : http://www.ictinnovations.com/                        *
 * Mail : nasir@ictinnovations.com                                 *
 * *************************************************************** */

use ICT\Core\Account;
use ICT\Core\Api;
use ICT\Core\Conf;
use ICT\Core\CoreException;
use ICT\Core\Program;
use ICT\Core\User;
use stdClass;

class AccountApi extends Api
{

  /**
   * Create a new account
   *
   * @url POST /accounts
   */
  public function create($data = array())
  {
    $this->_authorize('account_create');

    if (isset($data['type']) && !empty($data['type'])) {
      $oAccount = Account::load($data['type']);
    } else {
      $oAccount = new Account();
    }
    $this->set($oAccount, $data);

    if ($oAccount->save()) {
      return $oAccount->account_id;
    } else {
      throw new CoreException(417, 'Account creation failed');
    }
  }

  /**
   * List all available accounts
   *
   * @url GET /accounts
   */
  public function list_view($query = array())
  {
    $this->_authorize('account_list');
    return Account::search((array)$query);
  }

  /**
   * Gets the account by id
   *
   * @url GET /accounts/$account_id
   */
  public function read($account_id)
  {
    $this->_authorize('account_read');

    $oAccount = Account::load($account_id);
    return $oAccount;
  }

  /**
   * Gets the provisioning information by account id
   *
   * @url GET /accounts/$account_id/provisioning
   */
  public function provisioning($account_id)
  {
    $this->_authorize('account_read');

    $oAccount = $this->read($account_id);

    $oProvisioning = new stdClass();
    $oProvisioning->username = $oAccount->username;
    $oProvisioning->password = $oAccount->passwd;
    $oProvisioning->callerid = $oAccount->phone;
    $aProvisioning = Conf::get('provisioning');
    foreach ($aProvisioning as $field => $value) {
      $oProvisioning->{$field} = $value;
    }
    $oProvisioning->dialplan = array(
      'agent_login' => '*'.$oAccount->phone,
      'voicemail' => '*78',
    );
    $oProvisioning->account = $oAccount; // all other account informations

    return $oProvisioning;
  }

  /**
   * Update existing account
   *
   * @url PUT /accounts/$account_id
   */
  public function update($account_id, $data = array())
  {
    $this->_authorize('account_update');

    $oAccount = Account::load($account_id);
    $this->set($oAccount, $data);

    if ($oAccount->save()) {
      return $oAccount;
    } else {
      throw new CoreException(417, 'Account update failed');
    }
  }

  /**
   * Delete a account
   *
   * @url DELETE /accounts/$account_id
   */
  public function remove($account_id)
  {
    $this->_authorize('account_delete');

    $oAccount = Account::load($account_id);

    $result = $oAccount->delete();
    if ($result) {
      return $result;
    } else {
      throw new CoreException(417, 'Account delete failed');
    }
  }

  /**
   * Subscribe to selected program
   *
   * @url PUT /accounts/$account_id/programs/$program_name
   */
  public function subscribe($account_id, $program_name)
  {
    $this->_authorize('account_update');
    $this->_authorize('program_create');
    $this->_authorize('program_execute');
    $oAccount = Account::load($account_id);
    $oProgram = Program::load($program_name);

    return $oAccount->install_program($oProgram);
  }

  /**
   * Unsubscribe from selected program
   *
   * @url DELETE /accounts/$account_id/programs
   * @url DELETE /accounts/$account_id/programs/$program_name
   */
  public function unsubscribe($account_id, $program_name = 'all')
  {
    $this->_authorize('account_update');
    $this->_authorize('program_delete');
    $oAccount = Account::load($account_id);

    return $oAccount->remove_program($program_name);
  }

  /**
   * Associate account to selected user
   *
   * @url PUT /accounts/$account_id/users/$user_id
   */
  public function associate($account_id, $user_id)
  {
    $this->_authorize('account_create'); // instead of updated association is more like account creation
    $this->_authorize('user_update');
    $oAccount = Account::load($account_id);
    $oUser = new User($user_id);

    $oAccount->dissociate();
    return $oAccount->associate($oUser);
  }

  /**
   * Unsubscribe from selected program
   *
   * @url DELETE /accounts/$account_id/users
   */
  public function dissociate($account_id)
  {
    $this->_authorize('account_delete');
    $this->_authorize('user_update');
    $oAccount = Account::load($account_id);

    return $oAccount->dissociate();
  }

}

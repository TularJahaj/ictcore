<?php
namespace ICT\Core;
/* * ***************************************************************
 * Copyright © 2017 ICT Innovations Pakistan All Rights Reserved   *
 * Developed By: Nasir Iqbal                                       *
 * Website : http://www.ictinnovations.com/                        *
 * Mail : nasir@ictinnovations.com                                 *
 * *************************************************************** */
class Group
{
  /** @const */
  const COMPANY = -2;
  private static $table = 'contact_group';
  private static $primary_key = 'group_id';
  private static $fields = array(
      'group_id',
      'name',
      'contact_total',
      'description'
  );
  private static $read_only = array(
      'group_id',
      'contact_total'
  );

  /**
   * @property-read integer $group_id
   * @var integer
   */
  public $group_id = NULL;

  /** @var string */
  public $name = NULL;

  /** @var integer */
  private $contact_total = 0;

  /** @var string */
  public $description = '';

  /**
   * @property-read integer $user_id
   * owner id of current record
   * @var integer
   */
  public $user_id = NULL;

  public function __construct($group_id = NULL)
  {
    if (!empty($group_id) && $group_id > 0) {
      $this->group_id = $group_id;
      $this->load();
    } 
  }

  public static function search($aFilter = array())
  {
    $aGroup = array();
    $from_str = self::$table;
    $aWhere = array();
    foreach ($aFilter as $search_field => $search_value) {
      switch ($search_field) {
        case 'group_id':
          $aWhere[] = "$search_field = $search_value";
          break;
        case 'name':
          $aWhere[] = "$search_field LIKE '%$search_value%'";
          break;

        case 'user_id':
        case 'created_by':
          $aWhere[] = "created_by = '$search_value'";
          break;
        case 'before':
          $aWhere[] = "date_created <= $search_value";
          break;
        case 'after':
          $aWhere[] = "date_created >= $search_value";
          break;
      }
    }
    if (!empty($aWhere)) {
      $from_str .= ' WHERE ' . implode(' AND ', $aWhere);
    }

    $query = "SELECT group_id, name, contact_total FROM " . $from_str;
    Corelog::log("group search with $query", Corelog::DEBUG, array('aFilter' => $aFilter));
    $result = DB::query('group', $query);
    while ($data = mysql_fetch_assoc($result)) {
      $aGroup[] = $data;
    }

    return $aGroup;
  }

  // List Group Contact
  public function search_contact($aFilter = array(), $full = false)
  {
    $aFilter['group_id'] = $this->group_id;
    return Contact::search($aFilter, $full);
  }

  private function load()
  {
    $query = "SELECT * FROM " . self::$table . " WHERE group_id='%group_id%' ";
    $result = DB::query(self::$table, $query, array('group_id' => $this->group_id));
    $data = mysql_fetch_assoc($result);
    if ($data) {
      $this->group_id = $data['group_id'];
      $this->name = $data['name'];
      $this->contact_total = $data['contact_total'];
      $this->description = $data['description'];
      $this->user_id = $data['created_by'];
      Corelog::log("group loaded name: $this->name", Corelog::CRUD);
    } else {
      throw new CoreException('404', 'Group not found');
    }
  }

  public function delete()
  {
    Corelog::log("Group delete", Corelog::CRUD);
    return DB::delete(self::$table, 'group_id', $this->group_id);
  }

  public function __isset($field)
  {
    $method_name = 'isset_' . $field;
    if (method_exists($this, $method_name)) {
      return $this->$method_name();
    } else {
      return isset($this->$field);
    }
  }

  public function __get($field)
  {
    $method_name = 'get_' . $field;
    if (method_exists($this, $method_name)) {
      return $this->$method_name();
    } else if (!empty($field) && isset($this->$field)) {
      return $this->$field;
    }
    return NULL;
  }

  public function __set($field, $value)
  {
    $method_name = 'set_' . $field;
    if (method_exists($this, $method_name)) {
      $this->$method_name($value);
    } else if (empty($field) || in_array($field, self::$read_only)) {
      return;
    } else {
      $this->$field = $value;
    }
  }

  public function get_id()
  {
    return $this->group_id;
  }

  public function save()
  {
    $data = array(
        'group_id' => $this->group_id,
        'name' => $this->name,
        // read only 'contact_total' => $this->contact_total,
        'description' => $this->description
    );

    if (isset($data['group_id']) && !empty($data['group_id'])) {
      // update existing record
      $result = DB::update(self::$table, $data, 'group_id');
      Corelog::log("group updated: $this->group_id", Corelog::CRUD);
    } else {
      // add new
      $result = DB::update(self::$table, $data, false);
      $this->group_id = $data['contact_group_id']; // NOTE: DB::update using table name suffixed with _id as primary key
      Corelog::log("New group created: $this->group_id", Corelog::CRUD);
    }
    return $result;
  }
  
}
